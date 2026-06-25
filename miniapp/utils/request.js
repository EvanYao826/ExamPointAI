const app = getApp()

/**
 * 封装 wx.request
 * @param {string} url - 接口路径（不含 baseUrl）
 * @param {string} method - 请求方法
 * @param {object} data - 请求数据
 * @returns {Promise}
 */
function request(url, method = 'GET', data = {}) {
  return new Promise((resolve, reject) => {
    const header = {
      'Content-Type': 'application/json',
    }

    // 添加 token
    if (app.globalData.token) {
      header['Authorization'] = `Bearer ${app.globalData.token}`
    }

    wx.request({
      url: `${app.globalData.baseUrl}${url}`,
      method,
      data,
      header,
      success(res) {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          // token 过期，跳转登录页
          app.clearAuth()
          wx.redirectTo({ url: '/pages/login/login' })
          reject(new Error('登录已过期'))
        } else {
          const msg = res.data?.detail || '请求失败'
          wx.showToast({ title: msg, icon: 'none' })
          reject(new Error(msg))
        }
      },
      fail(err) {
        wx.showToast({ title: '网络错误', icon: 'none' })
        reject(err)
      },
    })
  })
}

module.exports = { request }
