/**
 * 配方渲染器 v2：遍历 KaTeX DOM tree → 精简 HTML
 * 目标：小程序的 rich-text 组件完美支持（sub/sup/table/span/div）
 */
import katex from "../node_modules/katex/dist/katex.mjs";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BASE = path.resolve(__dirname, "..");
const DATA_DIR = path.join(BASE, "mini-program", "miniprogram", "data");

// ═══════════════════════════════════════════════════════
// 1. DOM Tree → 精简 HTML 引擎
// ═══════════════════════════════════════════════════════

// 收集节点文本+结构标记
function walk(node) {
  if (!node) return "";
  if (Array.isArray(node)) return node.map(walk).join("");

  const classes = node.classes || [];
  const text = node.text || "";
  const children = node.children || [];
  const style = node.style || {};

  // 只处理文本的叶子节点
  if (text && children.length === 0) {
    return escapeText(text);
  }

  // ── 布局层：跳过 ──
  if (classes.includes("vlist-t") || classes.includes("vlist-r") ||
      classes.includes("vlist") || classes.includes("vlist-s") ||
      classes.includes("pstrut") || classes.includes("katex-strut") ||
      classes.includes("nulldelimiter") || classes.includes("katex-base") ||
      classes.includes("katex-html") || classes.includes("katex")) {
    if (classes.includes("katex")) {
      return `<span style="font-style:italic">${walk(children)}</span>`;
    }
    return walk(children);
  }

  // ── SVG 元素：跳过 ──
  if (classes.includes("svg-align") || classes.includes("hide-tail")) {
    return "";
  }

  // ── 分数 ──
  if (classes.includes("mfrac") || classes.includes("genfrac")) {
    return buildFraction(node);
  }

  // ── 上下标 ──
  if (classes.includes("msupsub")) {
    return buildSubSup(node);
  }

  // ── 根号 ──
  if (classes.includes("sqrt")) {
    return buildSqrt(node);
  }

  // ── 运算符（含积分、求和、lim 等） ──
  if (classes.includes("mop")) {
    return buildOperator(node);
  }

  // ── 间距 ──
  if (classes.includes("mspace")) {
    const margin = style.marginRight || "0.1667em";
    const w = parseFloat(margin) * 5; // em → px 约算
    if (w < 0.1) return "";
    return `<span style="display:inline-block;width:${w.toFixed(1)}px"></span>`;
  }

  // ── 分数线：跳过，由 buildFraction 处理 ──
  if (classes.includes("frac-line")) {
    return "";
  }

  // ── katex-sizing 缩放：透传子节点 ──
  if (classes.includes("katex-sizing") || classes.includes("reset-size6") ||
      classes.includes("mtight") || classes.includes("size3")) {
    return walk(children);
  }

  // ── 算子文本节点（mop 内的 l,i,m 等） ──
  if (classes.length === 0 && children.length === 0 && text) {
    return escapeText(text);
  }

  // ── 关系符 ──
  if (classes.includes("mrel")) {
    return `<span style="margin:0 2px">${walk(children)}</span>`;
  }

  // ── 二元运算符 ──
  if (classes.includes("mbin")) {
    return `<span style="margin:0 2px">${walk(children)}</span>`;
  }

  // ── 括号 ──
  if (classes.includes("mopen") || classes.includes("mclose")) {
    return walk(children);
  }

  // ── 普通数学对象（变量/数字） ──
  if (classes.includes("mord")) {
    return walk(children);
  }

  // ── 默认：透传 ──
  return walk(children);
}

// ─── 分数：<table> 实现 ───
function buildFraction(node) {
  // 在 vlist 中找 num 和 den
  const vlist = findChild(node, "vlist");
  if (!vlist || !vlist.children) return walk(node.children);

  let num = "", den = "";
  // vlist 的 children 按 top 排序：越负越高
  // [0] 通常是最低位置（分母），[2] 通常是最高的（分子）
  const items = vlist.children.filter(c => c && c.style && c.style.top);
  // 按 top 值排序（越负越高）
  const sorted = [...items].sort((a, b) => {
    return parseFloat(a.style.top || "0") - parseFloat(b.style.top || "0");
  });

  // 第一个（最负）= 分子，最后一个（最高/最正）= 分母
  // 但需要排除 frac-line
  const contentItems = [];
  for (const item of sorted) {
    const hasFracLine = findChild(item, "frac-line");
    if (!hasFracLine) {
      contentItems.push(item);
    }
  }

  if (contentItems.length >= 2) {
    num = walk(contentItems[0]);
    den = walk(contentItems[contentItems.length - 1]);
  } else if (contentItems.length === 1) {
    // 只有一个，可能是分子或分母
    num = walk(contentItems[0]);
    den = "";
  }

  if (!num && !den) return walk(node.children);

  return `<table style="display:inline-table;vertical-align:middle;margin:0 1px;border-collapse:collapse;font-size:0.85em">
  <tr><td style="text-align:center;border-bottom:1px solid #333;padding:0 3px;line-height:1.2">${num || "&nbsp;"}</td></tr>
  <tr><td style="text-align:center;padding:0 3px;line-height:1.2">${den || "&nbsp;"}</td></tr></table>`;
}

// ─── 上下标 ───
function buildSubSup(node) {
  // 在 vlist 中找上下标内容
  const vlist = findChild(node, "vlist");
  if (!vlist || !vlist.children) return walk(node.children);

  const items = vlist.children.filter(c => c && c.style && c.style.top);
  // 按 top 排序
  const sorted = [...items].sort((a, b) => {
    return parseFloat(a.style.top || "0") - parseFloat(b.style.top || "0");
  });

  // 判断是 sup 还是 sub
  const vlistT = findChild(node, "vlist-t");
  const hasVlistT2 = vlistT && vlistT.classes && vlistT.classes.includes("vlist-t2");

  if (hasVlistT2) {
    // 有 vlist-t2 → subscript（或 both）
    if (sorted.length >= 2) {
      return `<sub>${walk(sorted[1])}</sub><sup>${walk(sorted[0])}</sup>`;
    }
    return `<sub>${walk(sorted[0])}</sub>`;
  } else {
    // 无 vlist-t2 → superscript
    return `<sup>${walk(sorted[0])}</sup>`;
  }
}

// ─── 根号 ───
function buildSqrt(node) {
  const content = walk(node.children);
  return `<span style="border-top:1.5px solid #333;padding-top:0;margin:0 1px">√${content}</span>`;
}

// ─── 运算符（含积分/求和/lim/sin/log 等） ───
function buildOperator(node) {
  const classes = node.classes || [];

  // ── display mode 的 op-limits：\lim_{x→0}, \sum_{n=1}^\infty ──
  if (classes.includes("op-limits")) {
    const vlist = findChild(node, "vlist");
    if (!vlist || !vlist.children) return walk(node.children);

    const items = vlist.children.filter(c => c && c.style && c.style.top);
    const sorted = [...items].sort((a, b) => {
      return parseFloat(a.style.top || "0") - parseFloat(b.style.top || "0");
    });

    let op = "", sub = "", sup = "";
    for (const item of sorted) {
      const top = parseFloat(item.style.top || "0");
      const innerMop = findChild(item, "mop");
      if (innerMop) {
        // 这是运算符本身（top ≈ 0）
        op = walk(innerMop);
      } else if (top < -0.5) {
        // 下标（top 为负）
        sub = walk(item);
      } else if (top > 0.5) {
        // 上标（top 为正）
        sup = walk(item);
      } else {
        // top ≈ 0 但无 mop，可能是运算符的文本
        op = walk(item);
      }
    }

    let result = op;
    if (sub) result += `<sub>${sub}</sub>`;
    if (sup) result += `<sup>${sup}</sup>`;
    return `<span style="font-style:normal">${result}</span>`;
  }

  // ── inline mode：mop + msupsub ──
  const parts = [];
  const msupsub = findChild(node, "msupsub");

  // 运算符名在 node.text 上（如 "lim", "∫", "∑", "sin", "log"）
  if (node.text) {
    parts.push(escapeText(node.text));
  }

  for (const child of (node.children || [])) {
    if (child.classes && child.classes.includes("msupsub")) continue;
    parts.push(walk(child));
  }

  const op = parts.join("");

  if (msupsub) {
    const limits = buildSubSup(msupsub);
    return `<span style="font-style:normal">${op}${limits}</span>`;
  }

  return op;
}

// ─── 辅助函数 ───
function findChild(node, className) {
  if (!node) return null;
  if (node.classes && node.classes.includes(className)) return node;
  for (const child of (node.children || [])) {
    const found = findChild(child, className);
    if (found) return found;
  }
  return null;
}

function escapeText(t) {
  return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// ═══════════════════════════════════════════════════════
// 2. Markdown 公式提取 + 渲染
// ═══════════════════════════════════════════════════════

function renderFormula(latex, displayMode) {
  try {
    const tree = katex.__renderToDomTree(latex, {
      throwOnError: false,
      displayMode: !!displayMode,
      output: "html",
    });
    const html = walk(tree);
    if (displayMode) {
      return `<div style="text-align:center;margin:8px 0;overflow-x:auto">${html}</div>`;
    }
    return html;
  } catch (e) {
    return `<span style="color:#FF4D4F">${escapeText(latex)}</span>`;
  }
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/\n/g, "<br>");
}

function processMarkdown(md) {
  if (!md) return "";
  const parts = md.split(/(\$\$[^$]*?\$\$|\\\[[\s\S]*?\\\]|\$[^$]*?\$|\\\([\s\S]*?\\\))/g);
  let result = "";
  for (const part of parts) {
    if (!part) continue;
    let latex = "", displayMode = false;
    if (part.startsWith("$$") && part.endsWith("$$"))        { latex = part.slice(2, -2).trim(); displayMode = true; }
    else if (part.startsWith("\\[") && part.endsWith("\\]")) { latex = part.slice(2, -2).trim(); displayMode = true; }
    else if (part.startsWith("\\(") && part.endsWith("\\)")) { latex = part.slice(2, -2).trim(); }
    else if (part.startsWith("$") && part.endsWith("$"))     { latex = part.slice(1, -1).trim(); }
    else { result += escapeHtml(part); continue; }
    result += renderFormula(latex, displayMode);
  }
  return result;
}

// ═══════════════════════════════════════════════════════
// 3. 质量审查
// ═══════════════════════════════════════════════════════

function audit(questions) {
  const report = { total: 0, success: 0, error: 0, errors: [], samples: [] };
  for (const q of questions) {
    for (const field of ["stem_md", "answer_md", "solution_md"]) {
      const md = q[field] || "";
      const formulas = [];
      const re = /(\$\$[^$]*?\$\$|\\\[[\s\S]*?\\\]|\$[^$]*?\$|\\\([\s\S]*?\\\))/g;
      let m;
      while ((m = re.exec(md)) !== null) formulas.push(m[1]);
      for (const f of formulas) {
        report.total++;
        let latex = f;
        if (f.startsWith("$$") || f.startsWith("\\[")) latex = f.slice(2, -2).trim();
        else if (f.startsWith("\\(")) latex = f.slice(2, -2).trim();
        else if (f.startsWith("$")) latex = f.slice(1, -1).trim();
        try {
          katex.__renderToDomTree(latex, { throwOnError: true, displayMode: false, output: "html" });
          report.success++;
        } catch (e) {
          report.error++;
          if (report.errors.length < 20) {
            report.errors.push({ qid: q.id, field, latex: latex.slice(0, 60), error: e.message.slice(0, 80) });
          }
        }
      }
    }
    // 保存前3题的渲染样本
    if (report.samples.length < 3) {
      report.samples.push({
        id: q.id,
        stem: processMarkdown(q.stem_md || ""),
        answer: processMarkdown(q.answer_md || ""),
        solution: processMarkdown(q.solution_md || ""),
      });
    }
  }
  return report;
}

// ═══════════════════════════════════════════════════════
// 4. 主流程
// ═══════════════════════════════════════════════════════

function main() {
  const questions = JSON.parse(
    fs.readFileSync(path.join(DATA_DIR, "questions.json"), "utf-8")
  );

  // ── 阶段 A：审查 ──
  console.log("=".repeat(60));
  console.log("🔍 阶段 A：KaTeX 解析审查");
  console.log("=".repeat(60));
  const report = audit(questions);
  const passRate = report.total > 0 ? (report.success / report.total * 100).toFixed(1) : 0;
  console.log(`  总计公式: ${report.total}`);
  console.log(`  ✅ 通过: ${report.success} (${passRate}%)`);
  console.log(`  ❌ 失败: ${report.error}`);
  if (report.errors.length > 0) {
    console.log(`  前 ${Math.min(10, report.errors.length)} 个错误:`);
    for (const e of report.errors.slice(0, 10)) {
      console.log(`    Q${e.qid} ${e.field}: ${e.latex} → ${e.error}`);
    }
  }

  // ── 阶段 B：渲染样本 ──
  console.log(`\n${"=".repeat(60)}`);
  console.log("📝 阶段 B：渲染样本（前 3 题）");
  console.log("=".repeat(60));
  for (const s of report.samples) {
    console.log(`\n--- Q${s.id} 题目 ---`);
    console.log(s.stem.slice(0, 300));
    console.log(`--- Q${s.id} 答案 ---`);
    console.log(s.answer.slice(0, 200));
    console.log(`--- Q${s.id} 解析 ---`);
    console.log(s.solution.slice(0, 200));
  }

  // ── 阶段 C：全量渲染 ──
  console.log(`\n${"=".repeat(60)}`);
  console.log("⚙️ 阶段 C：全量渲染");
  console.log("=".repeat(60));
  let ok = 0, fail = 0;
  for (const q of questions) {
    try {
      q.stem_html = processMarkdown(q.stem_md);
      q.answer_html = processMarkdown(q.answer_md);
      q.solution_html = processMarkdown(q.solution_md);
      ok++;
    } catch (e) {
      fail++;
      console.error(`  Q${q.id} 渲染失败: ${e.message}`);
    }
  }
  console.log(`  ✅ ${ok} 题渲染成功, ❌ ${fail} 题失败`);

  // ── 阶段 D：输出 ──
  const outPath = path.join(DATA_DIR, "questions_with_html.js");
  const jsContent = "module.exports = " + JSON.stringify(questions, null, 2) + ";\n";
  fs.writeFileSync(outPath, jsContent, "utf-8");
  const sizeKb = fs.statSync(outPath).size / 1024;
  console.log(`\n📄 输出: ${outPath} (${sizeKb.toFixed(0)} KB)`);
  console.log("✅ 完成！");
}

main();