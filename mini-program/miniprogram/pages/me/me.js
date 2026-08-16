const db = require("../../utils/request")

// Use pre-transformed question map from request.js
const questionMap = db.questionDisplayMap || {}
db.getStats()

Page({
  data: {
    favorites: [],
    wrongs: [],
    tab: "favorite",
    stats: { favoriteCount: 0, wrongCount: 0 }
  },
  onShow() { this.loadList() },
  loadList() {
    const favorites = wx.getStorageSync("favorites") || []
    const wrongs = wx.getStorageSync("wrongs") || []
    this.setData({
      stats: { favoriteCount: favorites.length, wrongCount: wrongs.length },
      favorites: favorites.map((id) => questionMap[id] || {}),
      wrongs: wrongs.map((id) => questionMap[id] || {})
    })
  },
  switchTab(e) { this.setData({ tab: e.currentTarget.dataset.tab }) },
  goToQuestion(e) {
    wx.navigateTo({ url: `/pages/question-detail/question-detail?id=${e.currentTarget.dataset.id}&paperId=${e.currentTarget.dataset.paperId}` })
  },
  goToPapers() { wx.switchTab({ url: "/pages/papers/papers" }) },
  goToSearch() { wx.navigateTo({ url: "/pages/search/search" }) }
})