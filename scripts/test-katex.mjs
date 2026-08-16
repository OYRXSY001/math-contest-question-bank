import katex from "../node_modules/katex/dist/katex.mjs";
import fs from "fs";

const questions = JSON.parse(fs.readFileSync(
  "mini-program/miniprogram/data/questions.json", "utf-8"
));

// 测试 Q1 的解析
const md = questions[0].stem_md;

// 测试 行内公式
const inline = "\\int_0^1 f(xt)\\,\\mathrm dt";
console.log("=== 行内: " + inline + " ===");
try {
  const r = katex.renderToString(inline, { throwOnError: true, displayMode: false, output: "html" });
  console.log("OK:", r.slice(0, 150));
} catch(e) { console.log("ERROR:", e.message); }

// 测试 块级公式
const display = "\\iint_D\\frac{(x+y)\\ln\\left|1+\\frac yx\\right|}{\\sqrt{1-x-y}}\\,\\mathrm dx\\,\\mathrm dy";
console.log("\n=== 块级: " + display.slice(0, 60) + "... ===");
try {
  const r = katex.renderToString(display, { throwOnError: true, displayMode: true, output: "html" });
  console.log("OK, length:", r.length);
  console.log("First 300:", r.slice(0, 300));
} catch(e) { console.log("ERROR:", e.message); }

// 测试 简单的
console.log("\n=== 简单: \\frac{16}{15} ===");
try {
  const r = katex.renderToString("\\frac{16}{15}", { throwOnError: true, displayMode: false, output: "html" });
  console.log("OK, length:", r.length);
  console.log("Full:", r);
} catch(e) { console.log("ERROR:", e.message); }