const db = require("../../utils/request")

Page({
  data: { question: null, favorite: false, wrong: false, showSolution: false, showAnswer: false },
  onLoad(e) {
    if (e.id) this.fetchQuestion(parseInt(e.id))
  },
  fetchQuestion(id) {
    const q = db.getQuestion(id)
    this.setData({ question: q })
    if (q) {
      wx.setNavigationBarTitle({ title: `第${q.question_no}题` })
      this.checkStatus(q.id)
    }
  },
  checkStatus(id) {
    const favorites = wx.getStorageSync("favorites") || []
    const wrongs = wx.getStorageSync("wrongs") || []
    this.setData({
      favorite: favorites.includes(id),
      wrong: wrongs.includes(id)
    })
  },
  toggleFavorite() {
    let favorites = wx.getStorageSync("favorites") || []
    const id = this.data.question.id
    const idx = favorites.indexOf(id)
    if (idx >= 0) favorites.splice(idx, 1)
    else favorites.push(id)
    wx.setStorageSync("favorites", favorites)
    this.setData({ favorite: !this.data.favorite })
    wx.showToast({ title: this.data.favorite ? "已取消收藏" : "已收藏" })
  },
  toggleWrong() {
    let wrongs = wx.getStorageSync("wrongs") || []
    const id = this.data.question.id
    const idx = wrongs.indexOf(id)
    if (idx >= 0) wrongs.splice(idx, 1)
    else wrongs.push(id)
    wx.setStorageSync("wrongs", wrongs)
    this.setData({ wrong: !this.data.wrong })
    wx.showToast({ title: this.data.wrong ? "已取消错题" : "已加入错题" })
  },
  toggleSolution() { this.setData({ showSolution: !this.data.showSolution }) },
  toggleAnswer() { this.setData({ showAnswer: !this.data.showAnswer }) },
  copyStem() {
    wx.setClipboardData({ data: this.data.question.stem_md, success: () => wx.showToast({ title: "已复制" }) })
  },
  goToPaper() {
    if (this.data.question.paper_id) wx.navigateTo({ url: `/pages/paper-detail/paper-detail?id=${this.data.question.paper_id}` })
  }
})