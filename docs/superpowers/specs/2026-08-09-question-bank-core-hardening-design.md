---
title: 非数学 A 类真题库核心质量整改设计
slug: question-bank-core-hardening-design
summary: 补齐题目发布门槛、Excel 导入校验和试卷详情页入口，并收口生产媒体、图片、Admin、搜索与重复导入边界。
date: 2026-08-09
status: approved
---

# 非数学 A 类真题库核心质量整改设计

## 目标

本轮整改让现有 Django 题库满足三项要求：未完成内容复核的题目不能发布；导入命令能在写库前发现空数据、OCR 和图片问题；试卷详情页提供已有的 PDF 下载能力和吸顶题号导航。

最终审查追加五个收口：生产环境仅直出题目图片；导入图片必须在安全 Markdown 渲染后以 canonical 公开 URL 成为真实 `<img src>`；Admin inline 按提交后最终状态校验主知识点；搜索文本在局部更新和试卷改名后仍然当前；工作簿删除的题号被降为草稿而不删库。

整改沿用现有 Django 单体、SQLite、Markdown、KaTeX 和内置测试体系，不增加第三方依赖。

## 范围

本轮修改：

- 收紧 `Question.can_publish()` 和后台批量发布动作。
- 扩充 `import_question_bank` 的预检规则。
- 恢复试卷详情页的 PDF 下载按钮和题号导航样式。
- 限制 Caddy 仅直接服务 `MEDIA_ROOT/questions/`，其他媒体交由 Django。
- 校验 Markdown 实际渲染的图片 URL 与 Admin inline 提交后的主知识点状态。
- 刷新搜索文本，并将工作簿中移除的题号降为草稿。
- 为每项行为增加 Django 测试。

本轮不处理：

- 第 1—17 届真实题目录入。
- README、CI、异机备份和实际上线操作。
- 搜索算法、账号体系或数据库迁移。
- 合并 `non-math-a-question-bank` 到 `main`。

## 1. 发布门槛

### 1.1 可发布条件

`Question.can_publish()` 仅在下列条件全部满足时返回 `True`：

- 题目已经保存，具有主键。
- 当前状态为 `reviewed` 或 `published`。
- `text_checked`、`formula_checked`、`solution_checked` 均为真。
- `reviewed_by` 和 `reviewed_at` 均已填写。
- `unresolved_ocr_items` 和 `katex_errors` 均为零。
- `solution_md` 去除首尾空白后不为空。
- 关联表中恰好有一个 `is_primary=True` 的知识点。

数据库现有唯一约束继续负责“最多一个主知识点”，`can_publish()` 负责发布前的“必须有一个主知识点”。新建题目需要先保存为草稿或已复核状态，再关联主知识点，最后发布。

### 1.2 后台发布

后台批量发布动作只发布 `can_publish()` 返回真的题目。动作不自动填写审核人、复核时间或知识点，管理员需要明确完成这些字段。未通过题目保持原状态，后台消息显示发布数和跳过数。

模型继续在保存 `published` 状态时调用发布检查，防止绕过后台动作直接写入不合格题目。

### 1.3 Admin inline 最终状态

`QuestionKnowledgeInline` 使用自定义 `BaseInlineFormSet`。当父题目的待保存或当前状态为 `published` 时，formset 在排除标记 `DELETE` 的表单后，必须恰好有一条 `is_primary=True` 的有效关系。同次提交删除旧主知识点并新增另一个主知识点时，最终计数为一，允许保存。

## 2. Excel 导入预检

### 2.1 空数据

`source_inventory.xlsx` 和 `questions.xlsx` 都必须至少包含一行数据。只有表头的工作簿返回 `CommandError`，不再显示 `Dry-run passed: 0 papers, 0 questions`。

### 2.2 OCR 置信度

每道题必须填写 `ocr_confidence`，取值范围为 `0` 到 `1`，允许整数或小数。

当置信度低于 `0.90` 时：

- 如果 `text_checked=True`，表示人工已经逐字复核，允许 `unresolved_ocr_items=0`。
- 如果 `text_checked=False`，`unresolved_ocr_items` 必须大于零，导入人员需要显式记录未解决项。

题干、答案或解析中出现 Unicode 替换字符 `�` 或空方框 `□` 时，预检直接报错并指出 Excel 行号和字段。

### 2.3 题目图片

`image_files` 中声明的每个文件必须：

- 是相对 `MEDIA_ROOT` 的路径，位于 `questions/` 目录内，且路径不能逃逸。
- 使用 `.png`、`.jpg`、`.jpeg` 或 `.webp` 扩展名。
- 大小不超过 10 MiB。
- 文件头与扩展名对应：PNG 使用标准 8 字节签名，JPEG 以 `FF D8 FF` 开头，WebP 同时包含 `RIFF` 和 `WEBP` 标识。
- 其唯一接受的公开 Markdown URL 为 `settings.MEDIA_URL.rstrip("/") + "/" + relative_path_with_forward_slashes`，例如 `/media/questions/q1.png`。
- `stem_md`、`answer_md` 或 `solution_md` 经现有安全 Markdown 边界渲染后，该 canonical URL 必须出现在真实 `<img src>` 中；普通文本、代码块和普通链接都不算引用。

图片仍通过 Markdown 保存引用，数据库不新增图片字段。

### 2.4 错误与事务

新增校验沿用现有 `issues` 列表，错误信息包含工作簿类型、行号、字段和原因。dry-run 和正式导入执行相同预检；存在任何问题时不进入事务。正式导入继续使用单个 `transaction.atomic()`，保持整批回滚。

### 2.5 重复导入对账

库存工作簿中每个试卷对应的题目行，是该试卷当前有效题号集。同一 `transaction.atomic()` 中完成 upsert 后，数据库中该试卷不在本次题号集的旧题仅降为 `draft` 并更新 `updated_at`；不删除题目、知识点关系、收藏或错题记录。本次库存工作簿完全未包含的试卷不做任何处理。

## 3. 试卷详情页

试卷详情页标题区域在 `paper.pdf_file` 非空时显示“下载 PDF”按钮，链接到现有 `paper-download` 路由。没有 PDF 时不渲染按钮。

题号导航增加现有的 `question-number-nav` 类，让桌面端和手机端使用已经定义的吸顶、横向滚动样式。页面结构和视觉风格保持不变。

### 3.1 生产媒体边界

Caddy 仅为 `/media/questions/*` 启用 `handle_path` 与 `file_server`，并使用 `/srv/cmc-a/media/questions` 作为匹配根目录，使 `/media/questions/example.png` 正确解析到 `/srv/cmc-a/media/questions/example.png`。不存在通用 `/media/*` 直出路由；`/media/papers/*` 落入 Django，在生产 `DEBUG=0` 下返回 404。PDF 只通过 `paper-download` 控制器下载，`Paper.pdf_file` 保持原字段与存储路径。

### 3.2 搜索当前性

`Question.save()` 仍每次重建 `search_text`。调用者传入非 `None` 的 `update_fields` 时，模型将 `search_text` 合并进该集合再保存，保证重复导入更新内容时不留旧搜索文本。关键词过滤同时实时查询 `paper__title__icontains`，因此试卷改名后无需回写全部题目也能按新标题命中。

## 4. 测试策略

开发采用红、绿、重构循环。每项生产代码修改前先运行对应失败测试。

模型与后台测试覆盖：

- 缺少主知识点、复核时间或 `reviewed` 状态时不能发布。
- 完整复核并关联一个主知识点后可以发布。
- 批量动作跳过不合格题目。

导入测试覆盖：

- 空工作簿失败且不写库。
- OCR 置信度缺失、越界和低置信度未登记疑点时失败。
- 人工复核后的低置信度记录可以导入。
- 替换字符和空方框触发带行号错误。
- 图片路径逃逸、格式错误、文件头错误、超限和未被 Markdown 引用时失败。
- 相对图片 URL、纯文本命中和普通链接命中都失败；canonical `/media/questions/...` 的真实渲染图片通过。
- 重复导入刷新 `search_text`，删除的题号被降为草稿且所有关联记录保留。

页面测试覆盖：

- 有 PDF 时出现下载链接，无 PDF 时隐藏。
- 题号导航包含 `question-number-nav` 类。

部署、Admin 与查询测试还覆盖：

- Caddy 仅直出 `/media/questions/*`，并且匹配到题目图片文件夹。
- 已发布题删除唯一主知识点时 inline formset 无效，同次替换为新主知识点时有效。
- 试卷用 `update_fields=["title"]` 改名后，公开查询可按新标题命中其已发布题目。

每个任务先运行对应测试模块，再运行完整 Django 测试、`manage.py check` 和迁移漂移检查。

## 5. 完成标准

- 针对新增或修复行为的测试先按预期失败，再由最小实现修复；用于保留现有安全行为的回归测试可以先通过。
- 完整 Django 测试通过。
- `manage.py check` 无错误。
- `makemigrations --check --dry-run` 显示无模型变更。
- Git 工作区只包含本轮计划内文件。
