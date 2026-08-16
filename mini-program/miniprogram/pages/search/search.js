const db = require("../../utils/request")

Page({
  data: { query: "", results: [], searching: false },
  onLoad(e) {
    if (e.q) { this.setData({ query: e.q }); this.doSearch() }
  },
  onInput(e) { this.setData({ query: e.detail.value }) },
  doSearch() {
    if (!this.data.query.trim()) return
    const res = db.search(this.data.query)
    this.setData({ results: res.items })
  },
  goToQuestion(e) {
    wx.navigateTo({ url: `/pages/question-detail/question-detail?id=${e.currentTarget.dataset.id}&paperId=${e.currentTarget.dataset.paperId}` })
  },
  onClear() { this.setData({ query: "", results: [] }) }
})