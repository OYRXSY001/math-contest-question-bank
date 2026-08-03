---
title: 全国大学生数学竞赛非数学 A 类真题网站设计方案
slug: non-math-a-question-bank-design
summary: 面向第 1—17 届非数学 A 类初赛、决赛真题与详细解析的网站开发设计。
description: 规定页面、筛选、技术栈、数据结构、批量录题、OCR 校验、响应式布局、Windows 调试与低成本部署方案。网站只收录非数学 A 类范围内容。
date: 2026-08-03
status: review
---

## 项目范围与关键决策

网站只收录第 1—17 届全国大学生数学竞赛非数学 A 类范围内的初赛、决赛真题与详细解析。网站不提供数学专业类、非数学 B 类、课程、论坛、排行榜、支付或资讯功能。

实施基线：

- 第一版采用 Django 单体架构，先解决真题整理、公式渲染、搜索、PDF 下载、收藏和错题本。
- 题库类别固定为 `non_math_a`，前台不提供类别切换入口。
- 第 1—14 届按原卷保留“非数学类”等历史名称，并作为非数学 A 类历史范围收录；第 15—17 届按原卷显示“非数学 A 类”。导入人员逐卷核对 `original_category_label`，不批量改写原始标题。
- 初赛知识范围以高等数学为主。决赛原卷中的线性代数题属于非数学 A 类决赛内容，归入“决赛·线性代数”知识组，不扩展到其他竞赛类别。
- OCR 和公式识别只生成录入初稿。网站发布每道题前必须完成原卷对照和数学解析复核。

## 1. 页面清单与功能

| 页面 | 路由 | 功能 | 访问要求 |
| --- | --- | --- | --- |
| 首页 | `/` | 网站范围说明、关键词搜索、届数快捷入口、初赛/决赛入口 | 公开 |
| 真题库 | `/papers` | 试卷和题目列表；组合筛选；分页 | 公开 |
| 试卷详情 | `/papers/{id}` | 整卷在线阅读、题号导航、解析展开、PDF 下载 | 公开 |
| 单题详情 | `/questions/{id}` | 题干、详细解析、上下题切换、收藏、加入错题本 | 看题公开；用户操作需登录 |
| 搜索结果 | `/search?q={keyword}` | 搜索题干、答案、解析和知识点；保留筛选条件 | 公开 |
| 登录 | `/account/login` | 用户名和密码登录；登录后返回原页面 | 公开 |
| 注册 | `/account/register` | 创建普通用户 | 公开 |
| 我的收藏 | `/me/favorites` | 查看、筛选和取消收藏 | 登录用户 |
| 我的错题 | `/me/wrong-questions` | 查看、筛选和移出错题本 | 登录用户 |
| 内容后台 | `/admin` | 管理试卷、题目、知识点、用户和发布状态；对照原卷截图与网页渲染结果 | 管理员 |
| 404 | 系统路由 | 提供返回真题库和搜索入口 | 公开 |

### 1.1 首页

首页只承担入口功能：

- 一个关键词搜索框。
- 第 1—17 届快捷入口。
- 初赛、决赛两个入口。
- 明确显示“仅收录非数学 A 类范围”。

### 1.2 真题库

真题库同时支持试卷视图和题目视图。用户选择知识点或题型后，系统默认切换到题目结果；只选择届数或阶段时，可以继续显示试卷列表。

默认排序：

1. 届数从新到旧。
2. 同届先初赛、后决赛。
3. 试卷内按 `sort_order` 排序。

### 1.3 试卷详情

- 页面顶部显示届数、阶段、原始类别名称和 PDF 下载按钮。
- 页面主体连续显示整套题目。
- 解析默认收起。
- 题号导航点击后滚动到对应题目。
- 收藏和错题操作复用单题接口。

### 1.4 单题详情

- 搜索结果直接落到单题详情。
- 页面显示所属届数、阶段、题号、题型和知识点。
- 用户可以切换上一题、下一题。
- 未登录用户点击收藏或错题按钮时，系统跳转登录页并保存返回地址。

### 1.5 用户页面

收藏与错题本采用手动标记。第一版不建设在线答题和自动判分，避免为错题来源增加一套答题系统。

## 2. 筛选分类规则

### 2.1 届数

- 数据类型：整数。
- 有效范围：`1 <= edition <= 17`。
- 前台选项：“全部、第 1 届……第 17 届”。
- 资料缺失时显示“暂无收录”，不生成空白试卷或虚构题目。

### 2.2 阶段

| 数据值 | 页面名称 |
| --- | --- |
| `preliminary` | 初赛 |
| `final` | 决赛 |

数据库固定使用上述两个值。原始材料中的“预赛”“赛区赛”等名称保存在来源信息中，不参与前台筛选。

### 2.3 题型

每道题设置一个主题型：

| 数据值 | 页面名称 | 判断规则 |
| --- | --- | --- |
| `fill_blank` | 填空题 | 原卷要求直接填写结果 |
| `calculation` | 计算题 | 主要任务是求值、求极限、求积分或解方程 |
| `proof` | 证明题 | 主要任务是证明给定结论 |
| `comprehensive` | 综合题 | 含多个小问，或同时包含计算和证明任务 |

录题人员优先遵循原卷题型。原卷未标明题型时，再按主要作答任务分类。

### 2.4 知识点

每道题必须设置一个主知识点，可以设置多个次知识点。

#### 函数、极限与连续

- 函数性质
- 数列极限
- 函数极限
- 无穷小与无穷大
- 连续与间断点

#### 一元函数微分学

- 导数与微分
- 中值定理
- Taylor 公式
- 单调性与极值
- 凹凸性与拐点
- 渐近线

#### 一元函数积分学

- 不定积分
- 定积分
- 定积分应用
- 反常积分
- 含参积分

#### 多元函数微分学

- 多元函数极限与连续
- 偏导数与全微分
- 复合函数与隐函数
- 方向导数与梯度
- 多元函数极值
- Lagrange 乘数法

#### 重积分

- 二重积分
- 三重积分
- 坐标变换

#### 曲线积分与曲面积分

- 第一、第二类曲线积分
- 第一、第二类曲面积分
- Green 公式
- Gauss 公式
- Stokes 公式

#### 无穷级数

- 数项级数
- 幂级数
- Fourier 级数

#### 常微分方程

- 一阶微分方程
- 高阶微分方程
- 微分方程综合应用

#### 空间解析几何

- 向量与坐标
- 空间平面与直线
- 曲面与曲线

#### 决赛·线性代数

- 行列式与矩阵
- 线性方程组
- 向量组
- 特征值与特征向量
- 二次型

### 2.5 筛选组合

- 同一维度内采用“或”：选择“极限”和“连续”时，返回命中任一知识点的题目。
- 不同维度间采用“且”：第 17 届、初赛、证明题、Taylor 公式必须同时满足。
- 筛选状态写入 URL，刷新或分享链接后仍能恢复。
- 无结果时显示当前筛选条件和“清空筛选”按钮。

示例：

```text
/papers?edition=17&stage=preliminary&type=proof&knowledge=taylor-formula
```

## 3. 开发技术栈

### 3.1 新手简易方案：Django 单体

| 层级 | 技术 |
| --- | --- |
| 语言 | Python 3.13 |
| Web 框架 | Django 5.2 LTS |
| 数据库 | SQLite |
| 页面 | Django Template + Bootstrap 5 |
| 公式 | KaTeX |
| 用户与后台 | Django Auth + Django Admin |
| 搜索 | Django ORM `icontains` |
| 文件 | 服务器本地持久化目录 |

选择理由：

- 用户、Session、ORM 和管理后台可以直接复用。
- SQLite 不需要单独安装数据库服务。
- 数百道题使用数据库模糊查询即可。
- 前后端放在一个项目中，Windows 调试和低成本部署的步骤最少。

限制：多人并行开发前端、独立 App 或开放 API 成为明确需求时，再迁移到前后端分离方案。

### 3.2 正式前后端分离方案

前端：

- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia
- KaTeX

后端：

- Django 5.2
- Django REST Framework
- PostgreSQL
- Django Session + CSRF
- Django Admin

API：

```text
GET    /api/papers
GET    /api/papers/{id}
GET    /api/questions/{id}
GET    /api/search
POST   /api/questions/{id}/favorite
DELETE /api/questions/{id}/favorite
POST   /api/questions/{id}/wrong
DELETE /api/questions/{id}/wrong
```

同域部署使用 HttpOnly Session Cookie。第一版不引入 JWT、Redis、Elasticsearch、消息队列或微服务。

### 3.3 不采用纯静态 PDF 网站

纯静态页面可以下载 PDF，但收藏、错题、组合筛选、逐题搜索和内容校对都需要额外拼接工具。Django 单体实现这些功能所需代码更少，因此不采用纯静态方案。

## 4. 核心数据库结构

### 4.1 `users`

项目从第一天创建基于 Django `AbstractUser` 的用户模型，避免上线后迁移用户主键。

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `id` | BIGINT PK | 主键 |
| `username` | VARCHAR(150) | 唯一、必填 |
| `email` | VARCHAR(254) | 可空 |
| `password` | VARCHAR(128) | Django 密码哈希 |
| `is_staff` | BOOLEAN | 后台权限 |
| `is_active` | BOOLEAN | 账号状态 |
| `date_joined` | DATETIME | 注册时间 |
| `last_login` | DATETIME | 可空 |

### 4.2 `papers`

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `id` | BIGINT PK | 主键 |
| `edition` | SMALLINT | 第 1—17 届 |
| `stage` | VARCHAR(20) | `preliminary` 或 `final` |
| `scope_category` | VARCHAR(20) | 固定为 `non_math_a` |
| `original_category_label` | VARCHAR(50) | 原卷类别名称 |
| `title` | VARCHAR(200) | 页面标题 |
| `exam_year` | SMALLINT | 可空 |
| `pdf_file` | VARCHAR(500) | 可空 |
| `source_url` | VARCHAR(1000) | 可空 |
| `status` | VARCHAR(20) | `draft`、`reviewed`、`published` |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

约束：

```text
CHECK edition BETWEEN 1 AND 17
CHECK stage IN ('preliminary', 'final')
CHECK scope_category = 'non_math_a'
UNIQUE (edition, stage)
```

### 4.3 `questions`

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `id` | BIGINT PK | 主键 |
| `paper_id` | BIGINT FK | 所属试卷 |
| `question_no` | VARCHAR(20) | 原卷题号 |
| `sort_order` | SMALLINT | 试卷内排序 |
| `question_type` | VARCHAR(30) | 固定题型枚举 |
| `score` | DECIMAL(5,2) | 可空 |
| `stem_md` | TEXT | Markdown 题干 |
| `answer_md` | TEXT | 可空 |
| `solution_md` | TEXT | 详细解析 |
| `search_text` | TEXT | 去除排版符号后的搜索文本 |
| `source_page` | SMALLINT | 原卷页码 |
| `source_crop` | VARCHAR(500) | 私有校对截图路径 |
| `text_checked` | BOOLEAN | 题干已核对 |
| `formula_checked` | BOOLEAN | 公式已核对 |
| `solution_checked` | BOOLEAN | 解析已核对 |
| `reviewed_by_id` | BIGINT FK | 复核管理员，可空 |
| `reviewed_at` | DATETIME | 可空 |
| `status` | VARCHAR(20) | 发布状态 |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

约束：

```text
UNIQUE (paper_id, question_no)
```

### 4.4 `knowledge_points`

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `id` | BIGINT PK | 主键 |
| `name` | VARCHAR(100) | 名称 |
| `slug` | VARCHAR(100) | 唯一 URL 标识 |
| `subject` | VARCHAR(30) | `calculus` 或 `final_linear_algebra` |
| `parent_id` | BIGINT FK | 父知识点，可空 |
| `sort_order` | SMALLINT | 排序 |

### 4.5 `question_knowledge_points`

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `question_id` | BIGINT FK | 题目 |
| `knowledge_point_id` | BIGINT FK | 知识点 |
| `is_primary` | BOOLEAN | 是否主知识点 |

唯一约束：`(question_id, knowledge_point_id)`。

### 4.6 `favorites`

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `id` | BIGINT PK | 主键 |
| `user_id` | BIGINT FK | 用户 |
| `question_id` | BIGINT FK | 题目 |
| `created_at` | DATETIME | 收藏时间 |

唯一约束：`(user_id, question_id)`。

### 4.7 `wrong_questions`

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `id` | BIGINT PK | 主键 |
| `user_id` | BIGINT FK | 用户 |
| `question_id` | BIGINT FK | 题目 |
| `created_at` | DATETIME | 加入时间 |

唯一约束：`(user_id, question_id)`。

## 5. 第 1—17 届批量录入与准确率控制

### 5.1 资料清单

理论目标为 `17 届 × 初赛/决赛 = 34 套`。录入前建立 `source_inventory.xlsx`：

```text
edition
stage
original_category_label
source_file
source_url
source_type
question_count
has_answer
has_detailed_solution
review_status
```

缺少真实来源的试卷标记为“资料缺失”，不创建题目。

### 5.2 源文件处理顺序

1. Word 或 LaTeX：直接转换，不做 OCR。
2. 文本型 PDF：提取普通文字，单独处理公式。
3. 清晰扫描 PDF：使用文字 OCR 和公式识别。
4. 模糊扫描件：先寻找高清来源；无法替换时人工录入。

复杂坐标图、示意图和表格直接从原卷裁切。发布用图片和校对截图分开保存。

### 5.3 题目录入模板

使用 `questions.xlsx`，每题一行：

```text
edition
stage
question_no
sort_order
question_type
score
primary_knowledge
secondary_knowledge
stem_md
answer_md
solution_md
image_files
source_page
source_crop
ocr_confidence
text_checked
formula_checked
solution_checked
reviewer
reviewed_at
```

公式统一使用：

```latex
行内公式：\( f(x) \)

独立公式：
\[
\int_0^1 f(x)\,dx
\]
```

题目图片路径：

```text
media/questions/edition-01/preliminary/q03-figure-01.webp
```

校对截图路径：

```text
data/review/edition-01/preliminary/q03-source.png
```

`data/review` 不对公网开放。

### 5.4 自动校验

导入命令先执行 dry-run，检查：

- 届数在 1—17 范围内。
- 阶段、题型和知识点属于固定枚举。
- 同一试卷不存在重复题号。
- 题干和详细解析不为空。
- 原卷页码存在。
- Markdown 图片路径存在。
- LaTeX 定界符成对出现。
- 每个公式可以由 KaTeX 解析。
- PDF 文件扩展名和实际 MIME 类型均为 PDF。
- OCR 输出中不存在未处理的乱码、方框字符和低置信度标记。

程序重点标记下列易混淆字符：

```text
0 / O
1 / l / I
x / ×
- / =
d / ∂
Σ / ∑
上下标
积分和求和上下限
行列式竖线和绝对值
矩阵行列
导数撇号和阶数
```

自动校验通过后，导入程序按 `(edition, stage, question_no)` 执行幂等更新。任一题失败时，整套试卷事务回滚并报告 Excel 行号。

### 5.5 公式回渲染检查

每个公式按下列流程检查：

```text
原卷公式
  ↓
识别或人工录入 LaTeX
  ↓
KaTeX 回渲染
  ↓
原卷截图与网页结果并排对照
  ↓
管理员确认 formula_checked
```

KaTeX 解析成功只证明语法可渲染。校对人员仍需检查符号、上下标、括号范围、积分上下限、矩阵行列和向量格式。

### 5.6 两轮人工审核

第一轮核对原卷一致性：

- 题号和分值。
- 题干文字。
- 每个数学公式。
- 图片、表格和小问顺序。
- 简要答案。

第二轮核对详细解析：

- 最终答案。
- 推导步骤。
- 定理适用条件。
- 全文符号一致性。
- 主知识点和次知识点。

AI 可以协助生成解析草稿，但数学审核人员必须逐题确认。

### 5.7 发布门槛

后台只允许发布满足以下条件的题目：

```text
text_checked = true
formula_checked = true
solution_checked = true
unresolved_ocr_items = 0
katex_errors = 0
status = reviewed
```

验收标准：

| 项目 | 要求 |
| --- | --- |
| 试卷题目数量 | 与原卷一致 |
| 题号和分值 | 与原卷一致 |
| 公式语法 | 全部通过 KaTeX 渲染 |
| 公式内容 | 每个公式人工对照 |
| 图片 | 无缺失、无错题引用 |
| 详细解析 | 每题经过数学复核 |
| OCR 疑点 | 发布前清零 |

### 5.8 执行批次

先处理一套文本型 PDF 和一套扫描型 PDF，用两套试卷校准模板、公式规则和导入校验。此后按“提取一套、导入一套、校对一套、发布一套”的顺序推进，避免批量返工。

## 6. 电脑与手机自适应布局

| 区域 | 电脑端 | 手机端 |
| --- | --- | --- |
| 页面宽度 | 最大 1200px，居中 | 占满屏幕 |
| 筛选器 | 约 260px 左侧栏 | 顶部筛选按钮打开抽屉 |
| 内容区 | 主内容列 | 单列 |
| 题号导航 | 顶部或侧边 | 横向滚动吸顶栏 |
| 搜索框 | 顶部导航常驻 | 首页和列表顶部全宽 |
| 解析 | 点击展开 | 点击展开 |
| 收藏和错题 | 题目右上方 | 题目底部大按钮 |
| PDF 下载 | 页面顶部按钮 | 全宽按钮 |

断点：

- 手机：小于 `768px`。
- 平板：`768px—1199px`。
- 电脑：不小于 `1200px`。

样式要求：

- 图片使用 `max-width: 100%`。
- 宽公式在自身容器内横向滚动，不撑宽页面。
- 表格外层允许横向滚动。
- 手机按钮高度不低于 `44px`。
- 正文字号手机不小于 `16px`。
- 题号导航、筛选抽屉和解析按钮支持键盘操作及可见焦点。

## 7. Windows 调试与低成本部署

### 7.1 Django 单体本地调试

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

访问地址：

```text
网站：http://127.0.0.1:8000
后台：http://127.0.0.1:8000/admin
```

检查：

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

### 7.2 前后端分离本地调试

后端：

```powershell
.\backend\.venv\Scripts\python.exe backend\manage.py migrate
.\backend\.venv\Scripts\python.exe backend\manage.py runserver 8000
```

前端：

```powershell
Set-Location frontend
npm.cmd install
npm.cmd run dev
```

本地 PostgreSQL 可以使用 Windows 安装包或 Docker Desktop。开发环境只允许 `http://localhost:5173` 访问 API。

### 7.3 单服务器部署

最低成本方案使用一台 Linux 云服务器：

```text
Caddy
├── Django 静态文件或 Vue 构建结果
├── Django + Gunicorn
├── SQLite（简易方案）
└── PostgreSQL（前后端分离方案）
```

- Caddy 负责域名、HTTPS 和静态文件。
- Django 使用 Gunicorn 运行，不使用开发服务器。
- PDF、题目图片和数据库使用持久化目录。
- 每天把数据库和媒体目录备份到服务器之外。
- SQLite 适用于单实例、低并发版本；采用多实例或出现并发写入问题时切换 PostgreSQL。

### 7.4 前后端分开部署

- Vue 构建结果部署到 Cloudflare Pages。
- Django API 部署到低成本 Linux 服务器。
- PostgreSQL 初期与 API 同服务器部署。
- PDF 初期保存在 API 服务器；存储量或下载流量超出服务器容量时迁移对象存储。

若网站使用中国大陆服务器公开提供服务，部署前按接入商流程完成 ICP 备案。

## 8. 必备功能实现

### 8.1 在线看题

- 试卷详情连续显示整套题目。
- 单题详情支持上一题和下一题。
- 题干、图片、公式和解析来自结构化数据库。
- 解析默认收起。
- 未登录用户可以查看完整题目和解析。

### 8.2 公式渲染

- 数据库存 Markdown 和 LaTeX 源码，不把普通公式保存为截图。
- 页面使用 KaTeX 渲染行内公式和块级公式。
- 导入和发布时检查公式语法。
- 单个公式渲染失败时显示原始公式文本并记录错误，不影响整页题目。

### 8.3 PDF 下载

下载路由：

```text
/papers/{id}/download
```

响应头：

```http
Content-Type: application/pdf
Content-Disposition: attachment; filename="第17届-非数学A类-初赛.pdf"
```

- 后台只接受经过类型校验的 PDF。
- 文件名由后端生成，不使用用户上传的原始路径。
- 试卷没有 PDF 时隐藏下载按钮。

### 8.4 关键词搜题

搜索字段：

- 题干。
- 简要答案。
- 详细解析。
- 知识点名称。
- 试卷标题。

搜索规则：

- 去除关键词首尾空格。
- 空关键词直接返回搜索页，不执行全库查询。
- 关键词可以与届数、阶段、题型、知识点组合。
- 每页显示 20 条结果。
- 结果显示题干摘要、届数、阶段、题号和知识点。
- 第一版使用数据库模糊匹配，不增加独立搜索服务。

### 8.5 收藏与错题

- 收藏和错题使用独立按钮与独立数据表。
- 重复操作依靠唯一约束保持幂等。
- 未登录请求返回 `401` 或跳转登录页。
- 用户只能查看和修改自己的收藏、错题记录。

## 错误处理与验证

### 导入错误

- Excel 任一行校验失败时，整套试卷不入库。
- 错误报告包含文件名、工作表、行号、字段和原因。
- 重复导入使用更新键覆盖草稿，不产生重复题目。

### 页面错误

- 不存在或未发布的试卷、题目返回 404。
- PDF 缺失时不显示下载按钮。
- 搜索无结果时保留筛选条件。
- 收藏和错题接口检查登录状态与记录归属。

### 最小测试集

- 届数边界只接受 1 和 17 之间的整数。
- 初赛、决赛筛选结果正确。
- 同维度“或”、跨维度“且”的组合规则正确。
- 未发布题目不会出现在公开页面和搜索结果中。
- 重复收藏和重复加入错题不会创建第二条记录。
- 用户无法修改其他用户的收藏或错题。
- 合法 Excel 可以导入；非法题型、重复题号和缺失图片触发事务回滚。
- 测试公式可以由 KaTeX 渲染，宽公式不会撑破手机页面。
- PDF 下载响应包含正确的 MIME 类型和文件名。

## 参考资料

- [Django 5.2 LTS 发布说明](https://docs.djangoproject.com/en/dev/releases/5.2/)
- [Django 管理后台文档](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/)
- [Vue 与 TypeScript 官方指南](https://vuejs.org/guide/typescript/overview)
- [KaTeX 自动渲染文档](https://katex.org/docs/autorender)
- [Cloudflare Pages 部署 Vue](https://developers.cloudflare.com/pages/framework-guides/deploy-a-vue-site/)
- [非经营性互联网信息服务备案管理办法](https://www.miit.gov.cn/gyhxxhb/jgsj/cyzcyfgs/bmgz/xxtxl/art/2024/art_84a0cfa0ebd049bbbe751dca9a008e56.html)
- [第 14 届全国大学生数学竞赛初赛试题页面](https://www.cmathc.org.cn/csst/320.html)
- [第 15 届全国大学生数学竞赛报名规则](https://jwc.fudan.edu.cn/fd/e2/c27279a523746/page.htm)

