# 全国大学生数学竞赛题库

📚 基于 Django 的数学竞赛真题题库网站，收录第 1–17 届全国大学生数学竞赛（非数学类 A/B）初赛与决赛真题，共 **39 份试卷、254 道题**，公式使用 KaTeX 渲染，支持在线浏览题目与解析、下载试卷 PDF。

## 项目简介

本项目是面向全国大学生数学竞赛（非数学类 A/B）的真题题库系统，提供 **Web 网站**与**微信小程序**两个端：

- **Web 端（Django）**：在线浏览第 1–17 届初赛/决赛真题试卷与解析，公式使用 KaTeX 渲染，支持下载试卷 PDF，后台支持按届导入与管理题库数据。
- **小程序端（mini-program/）**：微信小程序版题库，内置题目数据与公式渲染组件，支持按试卷、知识点分类浏览和关键词搜索。

## ✨ 功能特性

- 🗂️ 收录第 1–17 届初赛/决赛真题，非数学类 A/B 双分类，共 39 份试卷、254 道题
- 📐 数学公式使用 KaTeX 渲染，Web 与小程序端均可正常显示
- 📄 在线浏览题目与详细解析，支持下载试卷 PDF
- 🔍 题目检索与知识点分类浏览
- 🛠️ 基于 openpyxl 工作簿的一键导入流程（试导入 dry-run + 正式导入 + 校验）
- 🧪 内置 104 项自动化测试与浏览器公式渲染检查脚本
- 📱 配套微信小程序端，题库数据内置、离线可用

## 技术栈

- Python 3.11+，Django 5.2，SQLite（单文件数据库）
- KaTeX 0.18 + Bootstrap 5（前端）
- openpyxl（题库导入）、Markdown（题干/解析渲染）
- Node.js 20+（可选：浏览器公式渲染检查）

## 目录结构

```
全国大学生18届/
├── manage.py              # Django 管理入口
├── db.sqlite3             # 数据库（含全部题目，已被 git 忽略）
├── config/                # 项目配置（settings 读取 .env）
├── question_bank/         # 题库主应用（模型、视图、导入命令）
├── accounts/              # 用户模块
├── mini-program/          # 微信小程序端（页面、组件、题库数据、云函数）
├── scripts/               # 公式渲染 / 检查脚本（render-*.mjs、test-*.mjs）
├── data/
│   ├── import/            # 各届导入工作簿（questions.xlsx、source_inventory.xlsx）
│   ├── review/            # 各届校验脚本、数据库备份、公式检查脚本
│   └── templates/         # 工作簿模板
├── media/papers/          # 各届试卷 PDF（edition-01 ~ edition-17）
├── static/                # 源码静态资源（KaTeX、Bootstrap 等）
├── staticfiles/           # collectstatic 产物
├── start.bat              # Windows 一键启动脚本
└── .env.example           # 环境变量示例
```

## 首次部署（个人电脑 / Windows）

1. **安装 Python**：安装 Python 3.11 或更高版本，勾选 “Add python.exe to PATH”。

2. **创建虚拟环境并安装依赖**（在项目根目录打开 PowerShell）：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. **安装前端资源**：

```powershell
npm install
```

4. **配置环境变量**：复制 `.env.example` 为 `.env`。个人本机使用保持默认即可：

```
DJANGO_DEBUG=1
DJANGO_SECRET_KEY=dev-only-key
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

5. **初始化数据库与静态文件**：

```powershell
python manage.py migrate
python manage.py collectstatic --noinput
```

6. **启动站点**：

```powershell
python manage.py runserver 127.0.0.1:8000
```

浏览器打开 <http://127.0.0.1:8000/papers/> 即可使用。

> 仓库内的 `db.sqlite3` 已包含全部导入数据；如果从全新环境初始化，migrate 之后直接使用现有数据库文件即可，无需重新导入。

## 日常使用

- 启动：`python manage.py runserver 127.0.0.1:8000`
- 浏览：<http://127.0.0.1:8000/papers/> 试卷列表，点击进入试卷可查看题目、解析并下载 PDF
- 测试：`python manage.py test question_bank`（当前 104 项用例应全部通过）
- 备份：直接复制 `db.sqlite3` 与 `media/` 目录即可（推荐每天/每次导入前备份）

## 导入新一届题库

以第 17 届为例，完整流程如下：

1. **准备试卷 PDF**：将初赛/决赛（A/B）PDF 放入

```
media/papers/edition-17/preliminary.pdf
media/papers/edition-17/preliminary-b.pdf
media/papers/edition-17/final.pdf
media/papers/edition-17/final-b.pdf
```

2. **生成导入工作簿**：参考 `data/review/edition-17/build_import_workbooks.py`（A 类）与 `build_import_workbooks_b.py`（B 类），运行后生成：

```
data/import/edition-17/questions.xlsx
data/import/edition-17/source_inventory.xlsx
data/import/edition-17-b/…
```

3. **试导入**：

```powershell
python manage.py import_question_bank `
  --inventory data\import\edition-17\source_inventory.xlsx `
  --questions data\import\edition-17\questions.xlsx --dry-run
```

4. **正式导入**（去掉 `--dry-run`）：

```powershell
python manage.py import_question_bank `
  --inventory data\import\edition-17\source_inventory.xlsx `
  --questions data\import\edition-17\questions.xlsx
```

5. **发布**：导入后试卷与题目处于 `reviewed` 状态，需要置为 `published` 才能在前台显示：

```powershell
.venv\Scripts\python.exe -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings'); import django; django.setup(); from question_bank.models import Paper, Question; Paper.objects.filter(edition=17).update(status='published'); Question.objects.filter(paper__edition=17).update(status='published')"
```

6. **验证**：跑测试，并用浏览器逐题检查公式渲染：

```powershell
python manage.py test question_bank
node data\review\edition-17\browser_math_check.cjs   # 需先启动站点
```

## 浏览器公式检查（可选）

`data/review/edition-XX/browser_math_check.cjs` 会打开每一道已发布题目，确认 KaTeX 正常渲染且页面无裸 `$` 残留。使用前需要：

```powershell
npm install -D playwright
npx playwright install chromium
```

然后启动站点并运行脚本（当前第 17 届：26 题、786 个公式，0 错误）。

## 开机自启（Windows）

**方式一：启动文件夹**（简单）

1. 在项目根新建 `start.bat`：

```bat
@echo off
cd /d C:\Users\35864\Desktop\全国大学生18届
start "" .venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

2. 按 `Win+R` 输入 `shell:startup`，把 `start.bat` 的快捷方式放进去。

**方式二：任务计划程序**（推荐）

1. 任务计划程序 → 创建任务；
2. 触发器：登录时；操作：启动程序，程序填 `.venv\Scripts\python.exe`，参数填 `manage.py runserver 127.0.0.1:8000`，起始于项目根目录；
3. 勾选“不管用户是否登录都要运行”可隐藏窗口。

## 局域网 / 生产部署（可选）

- **局域网访问**：`runserver 0.0.0.0:8000`，并把 `.env` 中 `DJANGO_ALLOWED_HOSTS` 加上本机局域网 IP。
- **Windows 生产**：`pip install waitress`，用 `waitress-serve --listen=0.0.0.0:8000 config.wsgi:application` 常驻。
- **Linux 生产**：`requirements.txt` 已含 gunicorn，可用 `gunicorn config.wsgi:application -b 0.0.0.0:8000`；关闭 DEBUG 时必须设置 `DJANGO_SECRET_KEY`（非 dev-only-key）。

## 数据说明

- 第 1–14 届仅有非数学类统一试卷；第 15 届初赛起分 A/B 类；第 16–17 届初赛与决赛均分 A/B 类。
- 第 17 届决赛 PDF 由公众号图片生成，非官方排版版本，其余各届均为官方/扫描 PDF。
- 数据库与媒体文件均被 git 忽略，代码仓库只包含程序源码；换机迁移时需一并拷贝 `db.sqlite3` 与 `media/`。
