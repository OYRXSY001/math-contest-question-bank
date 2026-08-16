import katex from "../node_modules/katex/dist/katex.mjs";

function showTree(node, depth) {
  if (!node || typeof node !== "object") return "  ".repeat(depth) + JSON.stringify(node);
  const pad = "  ".repeat(depth);
  if (Array.isArray(node)) {
    return node.map((n, i) => pad + "[" + i + "]:\n" + showTree(n, depth + 1)).join("\n");
  }
  let cls = node.classes || "";
  let txt = node.text || "";
  let style = node.style || "";
  let attrs = node.attributes || {};
  let info = [];
  if (cls) info.push("class=" + JSON.stringify(cls));
  if (txt) info.push("text=" + JSON.stringify(txt));
  if (style) info.push("style=" + JSON.stringify(style));
  if (Object.keys(attrs).length) info.push("attrs=" + JSON.stringify(attrs));
  let children = node.children || [];
  let result = pad + info.join(", ");
  if (children.length > 0) {
    result += "\n" + children.map((c, i) => pad + "  child[" + i + "]:\n" + showTree(c, depth + 2)).join("\n");
  }
  return result;
}

const tests = [
  "\\frac{16}{15}",
  "\\int_0^1 f(xt)\\,dt",
  "\\sqrt{1-x-y}",
  "x^2",
  "a_1",
  "\\lim_{x\\to0}",
];

for (const latex of tests) {
  try {
    const tree = katex.__renderToDomTree(latex, { throwOnError: false, displayMode: false, output: "html" });
    console.log(`\n=== ${latex} ===`);
    console.log(showTree(tree, 0));
  } catch (e) {
    console.log(`\n=== ${latex} ===`);
    console.log("ERROR:", e.message.slice(0, 80));
  }
}