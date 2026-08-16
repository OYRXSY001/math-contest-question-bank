const cloud = require("wx-server-sdk")
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database({ service: "postgresql" })
const $ = db.command

function stemPreview(md, len = 60) {
  if (!md) return ""
  return md.replace(/[\\$()\[\]{}^_]/g, "").substring(0, len)
}

async function listPapers(e) {
  let query = db.collection("papers").orderBy("year", "desc")
  if (e.year) query = query.where({ year: e.year })
  if (e.round) query = query.where({ round: e.round })
  const { data } = await query
    .skip(e.offset || 0)
    .limit(e.limit || 50)
    .get()
  return { items: data || [] }
}

async function getPaper(e) {
  const { data } = await db.collection("papers").doc(e.id).get()
  return data[0] || {}
}

async function listQuestions(e) {
  let query = db.collection("questions").orderBy("sort_order", "asc")
  if (e.paperId) query = query.where({ paper_id: e.paperId })
  const { data } = await query.skip(e.offset || 0).limit(e.limit || 50).get()
  return {
    items: (data || []).map((q) => ({ ...q, stem_preview: stemPreview(q.stem_md) }))
  }
}

async function getQuestion(e) {
  const { data } = await db.collection("questions").doc(e.id).get()
  const q = data[0] || {}
  const utils = require("../../../miniprogram/utils/request")
  q.stem_nodes = utils.mdToNodes(q.stem_md || "")
  q.answer_nodes = utils.mdToNodes(q.answer_md || "")
  q.solution_nodes = utils.mdToNodes(q.solution_md || "")
  q.stem_preview = stemPreview(q.stem_md)
  return q
}

async function search(e) {
  const kw = (e.keyword || "").trim()
  if (!kw) return { items: [] }
  const { data } = await db.collection("questions")
    .where({ search_text: db.RegExp({ regexp: kw, options: "i" }) })
    .orderBy("id", "asc")
    .limit(e.limit || 50)
    .get()
  return {
    items: (data || []).map((q) => ({ ...q, stem_preview: stemPreview(q.stem_md) }))
  }
}

async function getStats() {
  const [papers, questions, kps] = await Promise.all([
    db.collection("papers").count(),
    db.collection("questions").count(),
    db.collection("knowledge_points").count()
  ])
  return {
    papers: papers.total,
    questions: questions.total,
    knowledgePoints: kps.total
  }
}

async function getPaperKnowledgePoints(e) {
  const { data } = await db.collection("question_knowledge_points")
    .where({ question_id: $.in(await db.collection("questions")
      .where({ paper_id: e.paperId }).field({ id: true }).get().then(r => r.data.map(d => d.id))
    ) })
    .get()
  const kpidSet = new Set((data || []).map(r => r.knowledge_point_id))
  const { data: kpData } = await db.collection("knowledge_points")
    .where({ id: $.in([...kpidSet]) })
    .get()
  return { items: kpData || [] }
}

exports.main = async (e, ctx) => {
  const action = e.action || ""
  try {
    switch (action) {
      case "listPapers": return await listPapers(e)
      case "getPaper": return await getPaper(e)
      case "listQuestions": return await listQuestions(e)
      case "getQuestion": return await getQuestion(e)
      case "search": return await search(e)
      case "getStats": return await getStats()
      case "getPaperKnowledgePoints": return await getPaperKnowledgePoints(e)
      case "renderFormula": return { svg: e.latex }
      default: return { error: "unknown action: " + action }
    }
  } catch (err) {
    console.error(err)
    return { error: err.message }
  }
}