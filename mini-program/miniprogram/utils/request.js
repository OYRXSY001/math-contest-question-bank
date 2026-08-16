/** 本地数据加载 - 全国大学生数学竞赛真题库 */

// Load each dataset independently with its own error handling
function loadJSON(file) {
  try {
    return require(file)
  } catch (e) {
    console.warn("[request] 数据文件加载失败:", file, e)
    return []
  }
}

const papers = loadJSON("../data/papers.js")
// 使用原始 LaTeX 数据，运行时由 katex-mini 本地渲染公式（无服务端）
const questions = loadJSON("../data/questions.js")
const knowledgePoints = loadJSON("../data/knowledge_points.js")
const qkp = loadJSON("../data/qkp.js")

// ─── KaTeX 本地渲染引擎（katex-mini 打包版） ───
// lib/katex-bundle.js 由 esbuild 打包 katex-mini + katex 生成，纯本地无需构建 npm
let renderMathInText = null
try {
  const katexMini = require("../lib/katex-bundle.js")
  renderMathInText = (katexMini && katexMini.renderMathInText) ||
    (katexMini && katexMini.default && katexMini.default.renderMathInText) || null
  if (!renderMathInText) console.warn("[request] katex-mini 未找到 renderMathInText")
} catch (e) {
  console.warn("[request] katex-mini 加载失败，公式将回退为文本:", e)
}

// Build lookup maps
const questionMap = {}
questions.forEach((q) => { questionMap[q.id] = q })

const paperMap = {}
papers.forEach((p) => { paperMap[p.id] = p })

// Build question -> knowledge points map
const qKpMap = {}
qkp.forEach((r) => {
  if (!qKpMap[r.question_id]) qKpMap[r.question_id] = []
  qKpMap[r.question_id].push(r.knowledge_point_id)
})

// Enum value mappings (Django model -> display name)
const stageMap = {
  preliminary: "初赛",
  preliminary_b: "初赛（B类）",
  final: "决赛",
  final_b: "决赛（B类）"
}

const typeMap = {
  fill_blank: "填空题",
  calculation: "计算题",
  proof: "证明题",
  comprehensive: "综合题"
}

// Pre-compute per-paper question counts and total scores
const paperQuestionCounts = {}
const paperTotalScores = {}
questions.forEach((q) => {
  if (!paperQuestionCounts[q.paper_id]) paperQuestionCounts[q.paper_id] = 0
  paperQuestionCounts[q.paper_id]++
  if (!paperTotalScores[q.paper_id]) paperTotalScores[q.paper_id] = 0
  paperTotalScores[q.paper_id] += Number(q.score || 0)
})

// Transform a paper record to the display format expected by WXML templates
function transformPaper(p) {
  return {
    ...p,
    year: p.exam_year,
    round: stageMap[p.stage] || p.stage,
    question_count: paperQuestionCounts[p.id] || 0,
    total_score: paperTotalScores[p.id] || 0
  }
}

// Transform a question record to the display format
function transformQuestion(q) {
  const paper = paperMap[q.paper_id]
  return {
    ...q,
    question_type: typeMap[q.question_type] || q.question_type,
    paper_title: paper ? paper.title : "",
    stem_preview: stemPreview(q.stem_md)
  }
}

function stemPreview(md, len = 60) {
  if (!md) return ""
  // First render LaTeX to readable, then strip extra whitespace
  const rendered = latexToReadable(md)
  // Strip remaining LaTeX commands that may not have been caught
  return rendered.replace(/\s+/g, " ").trim().substring(0, len)
}

function getStats() {
  return {
    papers: papers.length,
    questions: questions.length,
    knowledgePoints: knowledgePoints.length
  }
}

function listPapers({ year, round, limit = 50, offset = 0 } = {}) {
  let list = [...papers]
  if (year) list = list.filter((p) => p.exam_year == year)
  if (round) {
    if (round === "初赛") list = list.filter((p) => p.stage === "preliminary")
    else if (round === "决赛") list = list.filter((p) => p.stage === "final")
    else if (round === "初赛（B类）") list = list.filter((p) => p.stage === "preliminary_b")
    else if (round === "决赛（B类）") list = list.filter((p) => p.stage === "final_b")
  }
  return { items: list.slice(offset, offset + limit).map(transformPaper) }
}

function getPaper(id) {
  const p = paperMap[id]
  return p ? transformPaper(p) : {}
}

function listQuestions({ paperId, limit = 50, offset = 0 } = {}) {
  let list = [...questions]
  if (paperId) list = list.filter((q) => q.paper_id === paperId)
  list.sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
  return {
    items: list.slice(offset, offset + limit).map((q) => ({
      ...transformQuestion(q),
      stem_preview: stemPreview(q.stem_md)
    }))
  }
}

function getQuestion(id) {
  const raw = questionMap[id]
  if (!raw) return {}
  const q = transformQuestion(raw)
  // 使用 katex-mini 本地渲染 LaTeX 公式（真实 KaTeX 排版质量）
  q.stem_nodes = mdToKatexNodes(raw.stem_md || "")
  q.answer_nodes = mdToKatexNodes(raw.answer_md || "")
  q.solution_nodes = mdToKatexNodes(raw.solution_md || "")
  q.stem_preview = stemPreview(q.stem_md)
  return q
}

/**
 * 将含 LaTeX 公式的文本转为 rich-text 节点
 * 优先 katex-mini（真实 KaTeX 排版）；未构建 npm 时回退为纯文本
 */
function mdToKatexNodes(md) {
  if (!md) return []
  if (!renderMathInText) return mdToNodes(md)
  try {
    const result = renderMathInText(md, {
      delimiters: [
        { left: "\\(", right: "\\)", display: false },
        { left: "\\[", right: "\\]", display: true },
        { left: "$", right: "$", display: false },
        { left: "$$", right: "$$", display: true }
      ],
      throwError: false
    })
    if (typeof result === "string") {
      // 无公式的纯文本
      return [{ type: "text", text: result }]
    }
    if (Array.isArray(result) && result.length > 0) return result
    return [{ type: "text", text: md }]
  } catch (e) {
    console.warn("[request] KaTeX 渲染失败，回退文本:", e)
    return mdToNodes(md)
  }
}

function search(keyword, { limit = 50 } = {}) {
  if (!keyword) return { items: [] }
  const kw = keyword.trim().toLowerCase()
  const results = questions.filter((q) =>
    (q.search_text || "").toLowerCase().includes(kw) ||
    (q.stem_md || "").toLowerCase().includes(kw) ||
    (q.question_no || "").includes(kw)
  ).slice(0, limit)
  return {
    items: results.map((q) => ({ ...transformQuestion(q), stem_preview: stemPreview(q.stem_md) }))
  }
}

function getPaperKnowledgePoints(paperId) {
  const qids = questions.filter((q) => q.paper_id === paperId).map((q) => q.id)
  const kpidSet = new Set()
  qids.forEach((qid) => {
    ;(qKpMap[qid] || []).forEach((kpid) => kpidSet.add(kpid))
  })
  return {
    items: knowledgePoints.filter((kp) => kpidSet.has(kp.id))
  }
}

// ─── LaTeX → Unicode 渲染引擎 ───

const LATEX_SYMBOLS = {
  // Greek letters
  "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
  "varepsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ", "vartheta": "θ",
  "iota": "ι", "kappa": "κ", "lambda": "λ", "mu": "μ", "nu": "ν",
  "xi": "ξ", "pi": "π", "varpi": "ϖ", "rho": "ρ", "varrho": "ϱ",
  "sigma": "σ", "varsigma": "ς", "tau": "τ", "upsilon": "υ",
  "phi": "ϕ", "varphi": "φ", "chi": "χ", "psi": "ψ", "omega": "ω",
  "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
  "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
  // Relations
  "le": "≤", "ge": "≥", "ne": "≠", "equiv": "≡", "approx": "≈",
  "sim": "∼", "simeq": "≃", "cong": "≅", "propto": "∝",
  "subset": "⊂", "supset": "⊃", "subseteq": "⊆", "supseteq": "⊇",
  "in": "∈", "notin": "∉", "ni": "∋", "forall": "∀", "exists": "∃",
  "perp": "⊥", "parallel": "∥", "mid": "∣",
  // Arrows
  "to": "→", "rightarrow": "→", "Rightarrow": "⇒", "longrightarrow": "→",
  "Longrightarrow": "⇒", "leftarrow": "←", "Leftarrow": "⇐",
  "leftrightarrow": "↔", "Leftrightarrow": "⇔",
  "uparrow": "↑", "downarrow": "↓",
  // Operators
  "times": "×", "cdot": "·", "circ": "∘", "ast": "∗",
  "otimes": "⊗", "oplus": "⊕", "odot": "⊙",
  "wedge": "∧", "vee": "∨", "cap": "∩", "cup": "∪",
  "setminus": "∖", "emptyset": "∅", "partial": "∂",
  "nabla": "∇", "infty": "∞", "prime": "′", "dprime": "″",
  "ell": "ℓ", "hbar": "ℏ", "imath": "ı", "jmath": "ȷ",
  "aleph": "ℵ", "Re": "ℜ", "Im": "ℑ",
  // Dots
  "cdots": "…", "ldots": "…", "vdots": "⋮", "ddots": "⋱",
  // Integrals & sums
  "int": "∫", "iint": "∬", "iiint": "∭", "oint": "∮",
  "sum": "∑", "prod": "∏", "coprod": "∐",
  // Functions (rendered as plain text)
  "sin": "sin", "cos": "cos", "tan": "tan", "cot": "cot",
  "sec": "sec", "csc": "csc",
  "arcsin": "arcsin", "arccos": "arccos", "arctan": "arctan",
  "sinh": "sinh", "cosh": "cosh", "tanh": "tanh",
  "log": "log", "ln": "ln", "lg": "lg",
  "lim": "lim", "max": "max", "min": "min", "sup": "sup", "inf": "inf",
  "det": "det", "dim": "dim", "deg": "deg",
  "exp": "exp", "mod": "mod",
  // Misc
  "colon": ":", "ldot": ".", "cdotp": "·",
  "quad": "  ", "qquad": "    ", " ": " ",
}

// Unicode superscripts & subscripts
const SUPERSCRIPTS = { "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "+": "⁺", "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾", "n": "ⁿ", "i": "ⁱ", "∞": "∞" }
const SUBSCRIPTS = { "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉", "+": "₊", "-": "₋", "=": "₌", "(": "₍", ")": "₎" }

function extractBraces(s, i) {
  // Starting from s[i] = '{', return { content, endIndex } for matching braces
  if (s[i] !== "{") return null
  let depth = 0, j = i
  while (j < s.length) {
    if (s[j] === "{") depth++
    else if (s[j] === "}") { depth--; if (depth === 0) break }
    j++
  }
  return { content: s.slice(i + 1, j), end: j }
}

function toUnicodeSup(text) {
  return text.split("").map(c => SUPERSCRIPTS[c] || c).join("")
}

function toUnicodeSub(text) {
  return text.split("").map(c => SUBSCRIPTS[c] || c).join("")
}

function parseOneToken(latex, i) {
  // Read a single LaTeX token: a character, a {group}, or a \command
  if (i >= latex.length) return { text: "", end: i }
  while (i < latex.length && (latex[i] === " " || latex[i] === "~")) i++ // skip spaces
  if (i >= latex.length) return { text: "", end: i }
  if (latex[i] === "{") {
    const group = extractBraces(latex, i)
    if (group) return { text: parseLatex(group.content, 0).text, end: group.end + 1 }
  }
  if (latex[i] === "\\") {
    return parseLatex(latex, i)
  }
  // Single character
  return { text: latex[i], end: i + 1 }
}

function parseLatex(latex, i = 0) {
  // Parse a LaTeX expression from index i, return { text, endIndex }
  let result = ""
  while (i < latex.length) {
    const c = latex[i]
    if (c === " " || c === "~") {
      result += " "
      i++
      continue
    }
    if (c === "{") {
      // Group: recursively parse content
      const group = extractBraces(latex, i)
      if (group) {
        result += parseLatex(group.content, 0).text
        i = group.end + 1
        continue
      }
    }
    if (c === "}") {
      // End of group
      break
    }
    if (c === "^") {
      // Superscript
      i++
      const next = parseLatex(latex, i)
      result += toUnicodeSup(next.text)
      i = next.end
      continue
    }
    if (c === "_") {
      // Subscript
      i++
      const next = parseLatex(latex, i)
      result += toUnicodeSub(next.text)
      i = next.end
      continue
    }
    if (c === "\\") {
      // Command
      i++
      let cmd = ""
      while (i < latex.length && /[a-zA-Z]/.test(latex[i])) {
        cmd += latex[i]; i++
      }
      if (cmd === "") {
        // Special character like \\, \,, \!, \;
        const special = { " ": " ", ",": " ", "!": "", ";": "  ", "\\": "\\" }
        result += special[latex[i]] || latex[i] || ""
        if (latex[i]) i++
        continue
      }
      if (cmd === "frac" || cmd === "dfrac" || cmd === "tfrac") {
        // \frac{a}{b} or \frac yx (single token each)
        var num = "", den = ""
        // Skip any spaces
        while (i < latex.length && (latex[i] === " " || latex[i] === "~")) i++
        // Parse numerator
        if (latex[i] === "{") { const n1 = extractBraces(latex, i); if (n1) { i = n1.end + 1; num = parseLatex(n1.content, 0).text } }
        else { const n1 = parseOneToken(latex, i); num = n1.text; i = n1.end }
        // Skip any spaces
        while (i < latex.length && (latex[i] === " " || latex[i] === "~")) i++
        // Parse denominator
        if (latex[i] === "{") { const n2 = extractBraces(latex, i); if (n2) { i = n2.end + 1; den = parseLatex(n2.content, 0).text; result += "(" + num + ")/(" + den + ")"; continue } }
        else if (i < latex.length && latex[i] !== "}" && latex[i] !== " " && latex[i] !== "^" && latex[i] !== "_") { const n2 = parseOneToken(latex, i); den = n2.text; i = n2.end; result += "(" + num + ")/(" + den + ")"; continue }
        result += cmd
      } else if (cmd === "sqrt") {
        // \sqrt{a} or \sqrt[n]{a}
        if (latex[i] === "[") {
          let j = i + 1
          while (j < latex.length && latex[j] !== "]") j++
          const root = parseLatex(latex.slice(i + 1, j), 0).text
          i = j + 1
          if (latex[i] === "{") {
            const n = extractBraces(latex, i)
            if (n) { i = n.end + 1; result += "∜(" + parseLatex(n.content, 0).text + ")" }
          } else { result += "∜(" + root + ")" }
        } else if (latex[i] === "{") {
          const n = extractBraces(latex, i)
          if (n) { i = n.end + 1; result += "√(" + parseLatex(n.content, 0).text + ")" }
        } else { result += "√" }
      } else if (cmd === "mathrm" || cmd === "text" || cmd === "mathbf" || cmd === "mathit" || cmd === "textrm" || cmd === "textbf" || cmd === "textit") {
        // \mathrm{...} \text{...} or \mathrm d (single token)
        while (i < latex.length && (latex[i] === " " || latex[i] === "~")) i++
        if (latex[i] === "{") {
          const n = extractBraces(latex, i)
          if (n) { i = n.end + 1; result += parseLatex(n.content, 0).text }
        } else {
          const n = parseOneToken(latex, i)
          result += n.text
          i = n.end
        }
      } else if (cmd === "left" || cmd === "right" || cmd === "big" || cmd === "Big" || cmd === "bigg" || cmd === "Bigg" || cmd === "bigl" || cmd === "bigr" || cmd === "biggl" || cmd === "biggr") {
        // \left( \right) etc. — just output the delimiter
        if (latex[i] === ".") { i++; continue }
        if (latex[i] === "|") { result += "|"; i++; continue }
        if (latex[i] === "(") { result += "("; i++; continue }
        if (latex[i] === ")") { result += ")"; i++; continue }
        if (latex[i] === "[") { result += "["; i++; continue }
        if (latex[i] === "]") { result += "]"; i++; continue }
        if (latex[i] === "{") { result += "{"; i++; continue }
        if (latex[i] === "}") { result += "}"; i++; continue }
        if (latex[i] === "\\" && latex[i + 1] === "{") { result += "{"; i += 2; continue }
        if (latex[i] === "\\" && latex[i + 1] === "}") { result += "}"; i += 2; continue }
        if (latex[i] === "\\") { i++; continue }
        result += latex[i] || ""; if (latex[i]) i++
      } else if (cmd === "operatorname") {
        if (latex[i] === "{") {
          const n = extractBraces(latex, i)
          if (n) { i = n.end + 1; result += n.content }
        }
      } else if (cmd === "over") {
        // Primitive fraction: a \over b
        result += "/"
      } else if (cmd === "binom" || cmd === "choose") {
        if (latex[i] === "{") { const n1 = extractBraces(latex, i); if (n1) { i = n1.end + 1; var ntext = parseLatex(n1.content, 0).text; if (latex[i] === "{") { const n2 = extractBraces(latex, i); if (n2) { i = n2.end + 1; result += "C(" + ntext + ", " + parseLatex(n2.content, 0).text + ")"; continue } } } }
        result += cmd
      } else if (cmd === "lim") {
        // \lim_{x \to 0}
        result += "lim"
        if (latex[i] === "_") {
          i++
          const next = parseLatex(latex, i)
          result += "₍" + next.text + "₎"
          i = next.end
        }
      } else if (cmd === "int" || cmd === "iint" || cmd === "iiint" || cmd === "oint" || cmd === "sum" || cmd === "prod") {
        result += LATEX_SYMBOLS[cmd] || cmd
        // Handle limits: \int_a^b or \sum_{n=0}^\infty
        if (latex[i] === "_") {
          i++
          const low = parseLatex(latex, i)
          result += "₍" + low.text + "₎"
          i = low.end
        }
        if (latex[i] === "^") {
          i++
          const high = parseLatex(latex, i)
          result += "⁽" + high.text + "⁾"
          i = high.end
        }
      } else if (cmd === "displaystyle" || cmd === "textstyle" || cmd === "scriptstyle" || cmd === "displaystyle" || cmd === "limits" || cmd === "nolimits") {
        // Style/layout commands — ignore
        continue
      } else if (cmd === "quad" || cmd === "qquad") {
        result += "  "
      } else if (cmd === "," || cmd === ";" || cmd === ":" || cmd === "!" || cmd === " ") {
        result += " "
      } else if (cmd === "\\") {
        result += "\\"
      } else {
        // Lookup symbol
        const sym = LATEX_SYMBOLS[cmd]
        if (sym) {
          result += sym
        } else {
          // Unknown command — just output the command name
          result += cmd
        }
      }
      continue
    }
    // Normal character
    result += c
    i++
  }
  return { text: result, end: i }
}

function latexToReadable(latex) {
  return parseLatex(latex.trim(), 0).text
}

/**
 * 将含 KaTeX 公式的 markdown 文本转为 rich-text 可用的节点格式
 * 现在使用预渲染的 HTML 数据，这里仅做兜底处理
 */
function mdToNodes(text) {
  if (!text) return []
  // 简单处理：将纯文本包装为 rich-text 节点
  const lines = text.split("\n")
  const nodes = []
  for (const line of lines) {
    if (!line.trim()) continue
    nodes.push({
      type: "div",
      style: "line-height:1.8;margin:4rpx 0;",
      children: [{ type: "text", text: line }]
    })
  }
  return nodes
}

// Build a pre-transformed question map for use by me.js etc.
const questionDisplayMap = {}
questions.forEach((q) => { questionDisplayMap[q.id] = transformQuestion(q) })

module.exports = {
  getStats,
  listPapers,
  getPaper,
  listQuestions,
  getQuestion,
  search,
  getPaperKnowledgePoints,
  mdToNodes,
  transformPaper,
  transformQuestion,
  questionMap,
  questionDisplayMap,
  stemPreview
}