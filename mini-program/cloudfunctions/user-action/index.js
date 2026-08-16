const cloud = require("wx-server-sdk")
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()
const $ = db.command

function stemPreview(md, len = 60) {
  if (!md) return ""
  return md.replace(/[\\$()\[\]{}^_]/g, "").substring(0, len)
}

async function getOpenid(e) {
  const { code } = e
  try {
    const res = await cloud.openapi.cloud.callOnce({
      data: { method: "POST", url: "https://api.weixin.qq.com/sns/jscode2session",
        data: { grant_type: "authorization_code", js_code: code } }
    })
    return { openid: res.result?.openid || "" }
  } catch (err) {
    return { openid: "" }
  }
}

async function toggleFavorite(e) {
  const { openid, questionId, favorite } = e
  const fav = await db.collection("user_favorites")
    .where({ openid, question_id: questionId }).get()
  if (favorite) {
    if (fav.data.length === 0) {
      await db.collection("user_favorites").add({
        data: { openid, question_id: questionId, created_at: db.serverDate() }
      })
    }
  } else {
    if (fav.data.length > 0) {
      await db.collection("user_favorites")
        .where({ openid, question_id: questionId }).remove()
    }
  }
  return { ok: true }
}

async function toggleWrong(e) {
  const { openid, questionId, wrong } = e
  const wr = await db.collection("user_wrongs")
    .where({ openid, question_id: questionId }).get()
  if (wrong) {
    if (wr.data.length === 0) {
      await db.collection("user_wrongs").add({
        data: { openid, question_id: questionId, created_at: db.serverDate() }
      })
    }
  } else {
    if (wr.data.length > 0) {
      await db.collection("user_wrongs")
        .where({ openid, question_id: questionId }).remove()
    }
  }
  return { ok: true }
}

async function checkStatus(e) {
  const { openid, questionId } = e
  if (!openid) return { favorite: false, wrong: false }
  const [fav, wr] = await Promise.all([
    db.collection("user_favorites").where({ openid, question_id: questionId }).count(),
    db.collection("user_wrongs").where({ openid, question_id: questionId }).count()
  ])
  return { favorite: fav.total > 0, wrong: wr.total > 0 }
}

async function getUserStats(e) {
  const { openid } = e
  if (!openid) return { favoriteCount: 0, wrongCount: 0 }
  const [fav, wr] = await Promise.all([
    db.collection("user_favorites").where({ openid }).count(),
    db.collection("user_wrongs").where({ openid }).count()
  ])
  return { favoriteCount: fav.total, wrongCount: wr.total }
}

async function getFavorites(e) {
  const { openid } = e
  const { data } = await db.collection("user_favorites")
    .where({ openid }).orderBy("created_at", "desc")
    .skip(e.offset || 0).limit(e.limit || 50).get()
  const qids = data.map((d) => d.question_id)
  const questions = {}
  for (const qid of qids) {
    try {
      const { data: qd } = await db.collection("questions").doc(qid).get()
      questions[qid] = qd[0] || {}
    } catch (err) { questions[qid] = {} }
  }
  return {
    items: data.map((f) => {
      const q = questions[f.question_id]
      return { id: f.question_id, question_no: q.question_no, question_type: q.question_type,
        stem_preview: stemPreview(q.stem_md), paper_id: q.paper_id, paper_title: "", ...q }
    })
  }
}

async function getWrongs(e) {
  const { openid } = e
  const { data } = await db.collection("user_wrongs")
    .where({ openid }).orderBy("created_at", "desc")
    .skip(e.offset || 0).limit(e.limit || 50).get()
  const qids = data.map((d) => d.question_id)
  const questions = {}
  for (const qid of qids) {
    try {
      const { data: qd } = await db.collection("questions").doc(qid).get()
      questions[qid] = qd[0] || {}
    } catch (err) { questions[qid] = {} }
  }
  return {
    items: data.map((w) => {
      const q = questions[w.question_id]
      return { id: w.question_id, question_no: q.question_no, question_type: q.question_type,
        stem_preview: stemPreview(q.stem_md), paper_id: q.paper_id, paper_title: "", ...q }
    })
  }
}

exports.main = async (e, ctx) => {
  const action = e.action || ""
  try {
    switch (action) {
      case "getOpenid": return await getOpenid(e)
      case "toggleFavorite": return await toggleFavorite(e)
      case "toggleWrong": return await toggleWrong(e)
      case "checkStatus": return await checkStatus(e)
      case "getUserStats": return await getUserStats(e)
      case "getFavorites": return await getFavorites(e)
      case "getWrongs": return await getWrongs(e)
      default: return { error: "unknown action: " + action }
    }
  } catch (err) {
    console.error(err)
    return { error: err.message }
  }
}