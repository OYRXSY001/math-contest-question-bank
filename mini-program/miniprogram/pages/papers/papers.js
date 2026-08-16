const db = require("../../utils/request")

Page({
  data: {
    papers: [],
    filters: { year: "全部", round: "全部" },
    years: ["全部"],
    rounds: ["全部", "初赛", "决赛"]
  },
  onShow() { this.fetchPapers() },
  onReady() {
    // Build year filter options from data
    const allYears = [...new Set(db.listPapers().items.map((p) => p.exam_year))].sort().reverse()
    this.setData({ years: ["全部", ...allYears] })
  },
  fetchPapers() {
    const params = {}
    if (this.data.filters.year !== "全部") params.year = this.data.filters.year
    if (this.data.filters.round !== "全部") params.round = this.data.filters.round
    const res = db.listPapers(params)
    this.setData({ papers: res.items })
  },
  onYearFilter(e) { this.setData({ "filters.year": e.currentTarget.dataset.val }); this.fetchPapers() },
  onRoundFilter(e) { this.setData({ "filters.round": e.currentTarget.dataset.val }); this.fetchPapers() },
  goToPaper(e) { wx.navigateTo({ url: `/pages/paper-detail/paper-detail?id=${e.currentTarget.dataset.id}` }) },
  onSearch() { wx.navigateTo({ url: "/pages/search/search" }) }
})