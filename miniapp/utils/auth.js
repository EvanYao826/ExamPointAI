/**
 * 微信登录工具
 * 用于需要用户身份时调用
 */

var app = getApp()

/**
 * 检查是否已登录
 */
function isLoggedIn() {
  return !!app.globalData.token
}

/**
 * 微信登录流程
 * 1. wx.login 获取 code
 * 2. 发送 code 给后端换 token
 * 3. 返回 token
 */
function wxLogin() {
  return new Promise(function (resolve, reject) {
    wx.login({
      success: function (res) {
        if (!res.code) {
          reject(new Error('wx.login 失败'))
          return
        }
        wx.request({
          url: app.globalData.baseUrl + '/api/v1/auth/wx/login',
          method: 'POST',
          data: { code: res.code },
          header: { 'Content-Type': 'application/json' },
          success: function (r) {
            if (r.statusCode === 200 && r.data && r.data.access_token) {
              app.setToken(r.data.access_token)
              resolve(r.data.access_token)
            } else {
              reject(new Error('登录失败'))
            }
          },
          fail: reject,
        })
      },
      fail: reject,
    })
  })
}

/**
 * 弹出登录确认框
 * 用户确认后调用 wx.login
 */
function requireLogin() {
  return new Promise(function (resolve, reject) {
    wx.showModal({
      title: '登录提示',
      content: '需要登录后才能使用此功能',
      confirmText: '微信登录',
      cancelText: '取消',
      success: function (res) {
        if (res.confirm) {
          wxLogin().then(resolve).catch(function (err) {
            wx.showToast({ title: '登录失败，请重试', icon: 'none' })
            reject(err)
          })
        } else {
          reject(new Error('用户取消登录'))
        }
      },
      fail: reject,
    })
  })
}

/**
 * 需要登录才能执行的操作
 * @param {Function} fn - 登录成功后执行的回调
 */
function withLogin(fn) {
  if (isLoggedIn()) {
    fn()
  } else {
    requireLogin().then(fn).catch(function () {})
  }
}

module.exports = {
  isLoggedIn: isLoggedIn,
  wxLogin: wxLogin,
  requireLogin: requireLogin,
  withLogin: withLogin,
}
