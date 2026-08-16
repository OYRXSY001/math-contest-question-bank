Component({
  properties: {
    latex: { type: String, value: "" },
    display: { type: Boolean, value: false },
    style: { type: String, value: "" }
  },
  data: {
    nodes: [],
    containerStyle: ""
  },
  watch: {
    latex(val) { this.updateNodes(val) }
  },
  methods: {
    updateNodes(latex) {
      if (!latex) {
        this.setData({ nodes: [], containerStyle: "" })
        return
      }
      const align = this.data.display ? "text-align:center;font-size:32rpx;padding:16rpx 0;" : "font-size:28rpx;color:#1677FF;"
      const text = this.data.display ? ("\\[" + latex + "\\]") : ("\\(" + latex + "\\)")
      this.setData({
        nodes: [{ type: "text", text }],
        containerStyle: align + this.data.style
      })
    }
  },
  lifetimes: {
    attached() { this.updateNodes(this.data.latex) }
  }
})