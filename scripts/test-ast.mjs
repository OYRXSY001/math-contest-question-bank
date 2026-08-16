import katex from "../node_modules/katex/dist/katex.mjs";

const tests = [
  "\\frac{16}{15}",
  "\\int_0^1 f(xt)\\,dt",
  "\\sqrt{1-x-y}",
  "x^2",
  "a_1",
  "\\lim_{x\\to0}",
  "\\iint_D\\frac{(x+y)\\ln\\left|1+\\frac yx\\right|}{\\sqrt{1-x-y}}\\,dx\\,dy",
];

function dumpAst(node, depth = 0) {
  const pad = "  ".repeat(depth);
  if (!node || typeof node !== "object") return pad + JSON.stringify(node);
  if (Array.isArray(node)) {
    return node.map((n) => dumpAst(n, depth)).join("\n");
  }
  const t = node.type || "?";
  const v = node.value !== undefined ? "=" + JSON.stringify(node.value) : "";
  const body = node.body ? " body:" + (Array.isArray(node.body) ? node.body.length + "items" : "1") : "";
  const sup = node.supsub ? " supsub" : "";
  const grep = node.group ? " group" : "";
  let line = `${pad}{${t}${v}${body}${sup}${grep}`;
  for (const k of ["num", "den", "body", "group", "supsub", "subscript", "superscript"]) {
    if (node[k]) {
      line += `\n${pad}  ${k}:`;
      if (Array.isArray(node[k])) {
        for (const item of node[k]) line += `\n${dumpAst(item, depth + 2)}`;
      } else {
        line += `\n${dumpAst(node[k], depth + 2)}`;
      }
    }
  }
  line += "}";
  return line;
}

for (const latex of tests) {
  try {
    const ast = katex.__parse(latex, {});
    console.log(`\n=== ${latex} ===`);
    console.log(dumpAst(ast));
  } catch (e) {
    console.log(`\n=== ${latex} ===`);
    console.log(`  ERROR: ${e.message}`);
  }
}