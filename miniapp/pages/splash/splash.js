var request = require('../../utils/request').request
var isLoggedIn = require('../../utils/auth').isLoggedIn

Page({
  onLoad() {
    var that = this
    setTimeout(function () {
      if (isLoggedIn()) {
        // 已登录，检查是否需要完善信息
        request('/api/v1/user/profile')
          .then(function (res) {
            if (!res.school_name) {
              wx.redirectTo({ url: '/pages/profile/profile' })
            } else {
              wx.switchTab({ url: '/pages/index/index' })
            }
          })
          .catch(function () {
            // token 失效等，直接去首页
            wx.switchTab({ url: '/pages/index/index' })
          })
      } else {
        wx.switchTab({ url: '/pages/index/index' })
      }
    }, 1200)
  },
})
