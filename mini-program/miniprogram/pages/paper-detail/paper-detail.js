const db = require("../../utils/request")

Page({
  data: { paper: null, questions: [], knowledgePoints: [] },
  onLoad(e) {
    if (e.id) this.fetchPaper(parseInt(e.id))
  },
  fetchPaper(id) {
    const paper = db.getPaper(id)
    const questions = db.listQuestions({ paperId: id })
    const kps = db.getPaperKnowledgePoints(id)
    this.setData({ paper, questions: questions.items, knowledgePoints: kps.items })
    if (paper) wx.setNavigationBarTitle({ title: paper.title || "试卷详情" })
  },
  goToQuestion(e) {
    wx.navigateTo({ url: `/pages/question-detail/question-detail?id=${e.currentTarget.dataset.id}&paperId=${e.currentTarget.dataset.paperId}` })
  },
  goToSearch(e) {
    wx.navigateTo({ url: `/pages/search/search?q=${encodeURIComponent(e.currentTarget.dataset.q)}` })
  }
})