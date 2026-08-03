import katex from "../node_modules/katex/dist/katex.mjs";

let input = "";
for await (const chunk of process.stdin) input += chunk;

const formulas = JSON.parse(input);
const errors = [];
formulas.forEach((formula, index) => {
  try {
    katex.renderToString(formula, { throwOnError: true, output: "html" });
  } catch (error) {
    errors.push({ index, message: String(error.message || error) });
  }
});
process.stdout.write(JSON.stringify(errors));
