App({
  globalData: {
    envId: "agent-d5gixdzged0e3c600",
    openid: null,
    userNick: null,
    maxEdition: 17
  },

  onLaunch() {
    this.initCloud();
    this.loadKaTeXFonts();
  },

  initCloud() {
    if (wx.cloud) {
      wx.cloud.init({
        env: this.globalData.envId,
        traceUser: true
      });
    } else {
      console.warn("wx.cloud 不可用，请检查基础库版本");
    }
  },

  /**
   * 加载 KaTeX 数学字体（本地打包，无需网络/CDN）
   * 与 katex-mini 的 index.wxss 中 font-family 名称保持一致
   */
  loadKaTeXFonts() {
    const fonts = [
      ["KaTeX_AMS", "normal", "normal", "KaTeX_AMS-Regular"],
      ["KaTeX_Caligraphic", "normal", "normal", "KaTeX_Caligraphic-Regular"],
      ["KaTeX_Caligraphic", "bold", "normal", "KaTeX_Caligraphic-Bold"],
      ["KaTeX_Fraktur", "normal", "normal", "KaTeX_Fraktur-Regular"],
      ["KaTeX_Fraktur", "bold", "normal", "KaTeX_Fraktur-Bold"],
      ["KaTeX_Main", "normal", "normal", "KaTeX_Main-Regular"],
      ["KaTeX_Main", "bold", "normal", "KaTeX_Main-Bold"],
      ["KaTeX_Main", "normal", "italic", "KaTeX_Main-Italic"],
      ["KaTeX_Main", "bold", "italic", "KaTeX_Main-BoldItalic"],
      ["KaTeX_Math", "normal", "italic", "KaTeX_Math-Italic"],
      ["KaTeX_Math", "bold", "italic", "KaTeX_Math-BoldItalic"],
      ["KaTeX_SansSerif", "normal", "normal", "KaTeX_SansSerif-Regular"],
      ["KaTeX_SansSerif", "bold", "normal", "KaTeX_SansSerif-Bold"],
      ["KaTeX_SansSerif", "normal", "italic", "KaTeX_SansSerif-Italic"],
      ["KaTeX_Script", "normal", "normal", "KaTeX_Script-Regular"],
      ["KaTeX_Size1", "normal", "normal", "KaTeX_Size1-Regular"],
      ["KaTeX_Size2", "normal", "normal", "KaTeX_Size2-Regular"],
      ["KaTeX_Size3", "normal", "normal", "KaTeX_Size3-Regular"],
      ["KaTeX_Size4", "normal", "normal", "KaTeX_Size4-Regular"],
      ["KaTeX_Typewriter", "normal", "normal", "KaTeX_Typewriter-Regular"]
    ];
    fonts.forEach(([family, weight, style, file]) => {
      wx.loadFontFace({
        global: true,
        family,
        source: `url("./assets/fonts/${file}.woff2")`,
        desc: { weight, style },
        fail: (err) => console.warn(`字体加载失败 ${file}:`, err)
      });
    });
  }
});
