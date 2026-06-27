var isLoggedIn = require('../../utils/auth').isLoggedIn

Page({
  data: {
    isLoggedIn: false,
  },

  onShow: function () {
    this.setData({ isLoggedIn: isLoggedIn() })
  },

  // 退出登录
  onLogout: function () {
    wx.showModal({
      title: '提示',
      content: '确定退出登录吗？',
      success: function (res) {
        if (res.confirm) {
          var app = getApp()
          app.clearAuth()
          wx.showToast({ title: '已退出', icon: 'success' })
          setTimeout(function () {
            wx.switchTab({ url: '/pages/index/index' })
          }, 1000)
        }
      },
    })
  },

  // 关于
  onAbout: function () {
    wx.showModal({
      title: '关于考点通',
      content: '考点通 v1.0.0\n大学生自己的刷题神器\n\n将老师发的题库一键转为在线刷题',
      showCancel: false,
    })
  },
})
