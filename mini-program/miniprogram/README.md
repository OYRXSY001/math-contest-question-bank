# 微信小程序（本地模式）

全国大学生数学竞赛真题库微信小程序，**纯本地模式**（无云开发、无服务端），数据与公式渲染全部在客户端完成。

## 公式渲染方案（KaTeX 本地渲染）

采用 [@rojer/katex-mini](https://github.com/chengazhen/katex-mini) 在小程序内直接解析 LaTeX → 生成 rich-text 节点，达到真实 KaTeX 排版质量（分数、根号、积分、上下标等）。

### 目录说明

| 路径 | 说明 |
|------|------|
| `lib/katex-bundle.js` | esbuild 打包的 katex-mini + katex 引擎（265KB，自包含、零外部依赖） |
| `lib/katex.wxss` | KaTeX 布局样式（app.wxss 已 @import） |
| `assets/fonts/*.woff2` | KaTeX 数学字体（20 个，254KB，本地打包） |

### 渲染流程

```
data/questions.js (LaTeX 原文)
        ↓ utils/request.js 的 mdToKatexNodes()
lib/katex-bundle.js 的 renderMathInText()
        ↓
rich-text 节点（katex 类名 + 内联样式）
        ↓ question-detail.wxml
<rich-text nodes="{{question.stem_nodes}}" />
```

支持的分隔符：`\(\)...\)`（行内）、`\[...\]`（行间）、`$...$`、`$$...$$`

### 重新打包 katex 引擎（升级版本后）

```powershell
cd mini-program\miniprogram
npm install          # 更新 @rojer/katex-mini / katex
npm run build:katex  # 重新生成 lib/katex-bundle.js
```

### 字体加载双保险

1. `app.js` 的 `loadKaTeXFonts()` 尝试用 `wx.loadFontFace` 加载本地 woff2（离线可用）
2. `lib/katex.wxss` 中保留 CDN @font-face 作为后备（开发模式 `urlCheck: false` 直接可用）
3. 生产上线时若需纯离线：把字体转 base64 内嵌到 wxss，或将 cdnjs.cloudflare.com 加入 downloadFile 合法域名

### 数据更新

```powershell
python export_data.py          # 从 Django 的 db.sqlite3 导出 JSON
cd miniprogram\data
convert_to_js.bat              # JSON → JS 模块
```
