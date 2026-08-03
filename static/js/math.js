document.addEventListener("DOMContentLoaded", () => {
  if (!window.renderMathInElement) return;
  window.renderMathInElement(document.body, {
    delimiters: [
      { left: "\\[", right: "\\]", display: true },
      { left: "\\(", right: "\\)", display: false },
    ],
    throwOnError: false,
    errorCallback: (message) => console.error("KaTeX:", message),
  });
});
