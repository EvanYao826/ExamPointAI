Page({
  onLoad() {
    // 直接跳转首页，不做登录
    setTimeout(() => {
      wx.switchTab({ url: '/pages/index/index' })
    }, 1200)
  },
})
