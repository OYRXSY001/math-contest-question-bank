/**
 * 测试 KaTeX SVG 渲染方案
 */
import katex from "../node_modules/katex/dist/katex.mjs";
import { JSDOM } from "jsdom";

// 先检查 jsdom 是否可用
try {
  const dom = new JSDOM('<!DOCTYPE html><div id="root"></div>');
  const document = dom.window.document;
  const root = document.getElementById("root");

  // 用 KaTeX 的 render 方法直接渲染到 DOM 元素
  katex.render("\\frac{16}{15}", root, {
    throwOnError: false,
    displayMode: false,
    output: "html",
  });

  console.log("Rendered HTML:");
  console.log(root.innerHTML);
  console.log("Length:", root.innerHTML.length);
} catch (e) {
  console.log("jsdom error:", e.message);
  // 尝试替代方案
  console.log("Using renderToString fallback");
  const html = katex.renderToString("\\frac{16}{15}", {
    throwOnError: false,
    displayMode: false,
    output: "html",
  });
  console.log("HTML:", html.slice(0, 200));
}