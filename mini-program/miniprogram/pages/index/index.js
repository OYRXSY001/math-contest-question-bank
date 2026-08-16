const db = require("../../utils/request")

Page({
  data: {
    stats: { papers: 0, questions: 0, knowledgePoints: 0 },
    latestPapers: []
  },
  onShow() {
    const stats = db.getStats()
    const latest = db.listPapers({ limit: 6 })
    this.setData({ stats, latestPapers: latest.items })
  },
  goSearch(e) {
    wx.navigateTo({ url: `/pages/search/search?q=${encodeURIComponent(e.currentTarget.dataset.q)}` })
  },
  goToPapers() { wx.switchTab({ url: "/pages/papers/papers" }) },
  goToPaper(e) {
    wx.navigateTo({ url: `/pages/paper-detail/paper-detail?id=${e.currentTarget.dataset.id}` })
  },
  goToMe() { wx.switchTab({ url: "/pages/me/me" }) }
})