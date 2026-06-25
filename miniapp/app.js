App({
  globalData: {
    baseUrl: 'http://localhost:8000',
    token: '',
    userInfo: null,
  },

  onLaunch() {
    // 尝试从本地缓存恢复登录状态
    const token = wx.getStorageSync('token')
    if (token) {
      this.globalData.token = token
    }
  },

  // 设置 token
  setToken(token) {
    this.globalData.token = token
    wx.setStorageSync('token', token)
  },

  // 清除登录状态
  clearAuth() {
    this.globalData.token = ''
    this.globalData.userInfo = null
    wx.removeStorageSync('token')
  },
})
