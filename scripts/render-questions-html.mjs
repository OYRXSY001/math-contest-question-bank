/**
 * 用 KaTeX 将题目中的 LaTeX 公式预渲染为 HTML（内联样式 + 字体回退）
 * 输出给小程序 rich-text 直接使用
 *
 * 由于小程序不支持 @font-face 加载 KaTeX 字体，使用 Times New Roman 回退
 * 配合 KaTeX 的布局结构，达到接近网站的渲染效果
 *
 * 用法: node scripts/render-questions-html.mjs
 */
import katex from "../node_modules/katex/dist/katex.mjs";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BASE = path.resolve(__dirname, "..");
const DATA_DIR = path.join(BASE, "mini-program", "miniprogram", "data");

// ═══════════════════════════════════════════════
// 1. 解析 KaTeX CSS
// ═══════════════════════════════════════════════

const katexCss = fs.readFileSync(
  path.join(BASE, "node_modules", "katex", "dist", "katex.min.css"),
  "utf-8"
);

function parseCSS(css) {
  const rules = [];
  css = css.replace(/\/\*[\s\S]*?\*\//g, "");
  const blockRegex = /([^{]+)\{([^}]+)\}/g;
  let match;
  while ((match = blockRegex.exec(css)) !== null) {
    const rawSelector = match[1].trim();
    const declarations = match[2].trim();
    if (!declarations) continue;
    if (/:|@|>|\+|~|#/.test(rawSelector)) continue;
    for (const sel of rawSelector.split(",").map((s) => s.trim())) {
      if (!sel) continue;
      const parts = sel.trim().split(/\s+/);
      const last = parts[parts.length - 1];
      if (!last) continue;
      const tagMatch = last.match(/^([a-zA-Z0-9]+)/);
      const tag = tagMatch ? tagMatch[1] || "" : "";
      const classes = [...last.matchAll(/\.([\w-]+)/g)].map((m) => m[1]);
      if (classes.length === 0 && !tag) continue;
      const specificity = classes.length * 100 + (tag ? 1 : 0);
      rules.push({ specificity, tag, classes, declarations });
    }
  }
  return rules;
}

const cssRules = parseCSS(katexCss);
console.log(`📐 解析了 ${cssRules.length} 条 CSS 规则`);

function mergeStyles(existing, additions) {
  if (!additions) return existing || "";
  const map = {};
  const all = ((existing || "") + ";" + additions).split(";");
  for (const d of all) {
    const idx = d.indexOf(":");
    if (idx > 0) {
      const prop = d.slice(0, idx).trim().toLowerCase();
      const val = d.slice(idx + 1).trim();
      if (prop && val) map[prop] = val;
    }
  }
  return Object.entries(map).map(([k, v]) => `${k}:${v}`).join(";");
}

function inlineKaTeXStyles(html) {
  // 移除不可见的 MathML 输出
  html = html.replace(/<span class="katex-mathml">[\s\S]*?<\/span>/g, "");

  return html.replace(/<(\w+)([^>]*?)>/gs, (match, tag, attrs) => {
    if (match.endsWith("/>") || tag === "!--") return match;

    const classMatch = attrs.match(/\sclass="([^"]*)"/);
    const classList = classMatch ? classMatch[1].split(/\s+/) : [];

    // 跳过 SVG 元素（小程序 rich-text 不支持 SVGs）
    if (["svg", "path", "line", "rect", "circle", "ellipse", "defs", "g", "use", "symbol", "clipPath", "mask", "linearGradient", "radialGradient", "stop", "feGaussianBlur", "feColorMatrix", "filter", "pattern", "text", "tspan", "marker", "polygon", "polyline", "image"].includes(tag)) {
      return match;
    }

    const styleMatch = attrs.match(/\sstyle="([^"]*)"/);
    const existingStyle = styleMatch ? styleMatch[1] : "";

    const matchingRules = cssRules
      .filter((r) => {
        if (r.tag && r.tag !== tag && r.tag !== "*") return false;
        return r.classes.every((c) => classList.includes(c));
      })
      .sort((a, b) => a.specificity - b.specificity);

    let allDeclarations = existingStyle;
    for (const rule of matchingRules) {
      allDeclarations = mergeStyles(allDeclarations, rule.declarations);
    }

    // 为 .katex 元素添加字体回退
    if (classList.includes("katex") && !allDeclarations.includes("font-family")) {
      allDeclarations = mergeStyles(allDeclarations, "font-family:'Times New Roman',Times,serif;font-size:1.1em;line-height:1.2");
    }
    // 为 .mord, .mbin, .mrel 等添加 math 字体样式
    if (classList.some(c => ["mord", "mbin", "mrel", "mopen", "mclose", "mpunct", "minner", "mop", "mspace", "mlongdiv"].includes(c))) {
      allDeclarations = mergeStyles(allDeclarations, "font-family:'Times New Roman',Times,serif");
    }

    if (allDeclarations !== existingStyle) {
      if (styleMatch) {
        const before = attrs.slice(0, styleMatch.index);
        const after = attrs.slice(styleMatch.index + styleMatch[0].length);
        return `<${tag}${before} style="${allDeclarations}"${after}>`;
      }
      return `<${tag}${attrs} style="${allDeclarations}">`;
    }
    return match;
  });
}

// ═══════════════════════════════════════════════
// 2. 渲染 LaTeX → HTML
// ═══════════════════════════════════════════════

function renderFormula(latex, displayMode) {
  try {
    const html = katex.renderToString(latex, {
      throwOnError: false,
      displayMode: !!displayMode,
      output: "html",
    });
    let result = inlineKaTeXStyles(html);
    // 移除所有残留的 SVG / MathML 标签
    result = result.replace(/<svg[\s\S]*?<\/svg>/g, "");
    result = result.replace(/<annotation[\s\S]*?<\/annotation>/g, "");
    result = result.replace(/<semantics[\s\S]*?<\/semantics>/g, "");
    result = result.replace(/<math[\s\S]*?<\/math>/g, " ");
    // 块级公式居中
    if (displayMode) {
      result = `<div style="text-align:center;margin:0.5em 0;padding:0.2em 0;overflow-x:auto;white-space:nowrap;">${result}</div>`;
    }
    return result;
  } catch (e) {
    console.warn(`  ⚠ 渲染失败: ${latex.slice(0, 50)}... (${e.message})`);
    return `<span style="color:#FF4D4F;">${latex}</span>`;
  }
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/\n/g, "<br>");
}

function processMarkdown(md) {
  if (!md) return "";
  const parts = md.split(/(\$\$[^$]*?\$\$|\\\[[\s\S]*?\\\]|\$[^$]*?\$|\\\([\s\S]*?\\\))/g);
  let result = "";
  for (const part of parts) {
    if (!part) continue;
    let latex = "", displayMode = false;
    if (part.startsWith("$$") && part.endsWith("$$"))      { latex = part.slice(2, -2).trim(); displayMode = true; }
    else if (part.startsWith("\\[") && part.endsWith("\\]")) { latex = part.slice(2, -2).trim(); displayMode = true; }
    else if (part.startsWith("\\(") && part.endsWith("\\)")) { latex = part.slice(2, -2).trim(); }
    else if (part.startsWith("$") && part.endsWith("$"))    { latex = part.slice(1, -1).trim(); }
    else { result += escapeHtml(part); continue; }
    result += renderFormula(latex, displayMode);
  }
  return result;
}

// ═══════════════════════════════════════════════
// 3. 主流程
// ═══════════════════════════════════════════════

function main() {
  const questions = JSON.parse(
    fs.readFileSync(path.join(DATA_DIR, "questions.json"), "utf-8")
  );

  let updated = 0, errors = 0;

  for (const q of questions) {
    try {
      q.stem_html = processMarkdown(q.stem_md);
      q.answer_html = processMarkdown(q.answer_md);
      q.solution_html = processMarkdown(q.solution_md);
      updated++;
    } catch (e) {
      console.error(`Q${q.id} 错误:`, e.message);
      errors++;
    }
  }

  // 输出为 JS 模块格式
  const outPath = path.join(DATA_DIR, "questions_with_html.js");
  const jsContent = "module.exports = " + JSON.stringify(questions, null, 2) + ";\n";
  fs.writeFileSync(outPath, jsContent, "utf-8");

  const sizeKb = fs.statSync(outPath).size / 1024;
  const original = JSON.parse(fs.readFileSync(path.join(DATA_DIR, "questions.json"), "utf-8"));
  const origKb = JSON.stringify(original).length / 1024;

  // 验证几个例子
  console.log(`\n✅ 完成！处理 ${updated} 题，${errors} 错误`);
  console.log(`📄 输出: ${outPath} (${sizeKb.toFixed(0)} KB, 原 ${origKb.toFixed(0)} KB)`);
  console.log(`\n📝 示例渲染:`);
  for (const q of questions.slice(0, 3)) {
    const snippet = (q.stem_html || "").replace(/<[^>]+>/g, "").slice(0, 80);
    console.log(`  Q${q.id}: ${snippet}...`);
  }
  console.log(`\n👉 现在打开微信开发者工具查看效果！`);
}

main();