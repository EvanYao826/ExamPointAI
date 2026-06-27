var app = getApp()

/**
 * 封装 wx.request
 * @param {string} url - 接口路径（不含 baseUrl）
 * @param {string} method - 请求方法
 * @param {object} data - 请求数据
 * @returns {Promise}
 */
function request(url, method, data) {
  method = method || 'GET'
  data = data || {}

  return new Promise(function (resolve, reject) {
    var header = {
      'Content-Type': 'application/json',
    }

    if (app.globalData.token) {
      header['Authorization'] = 'Bearer ' + app.globalData.token
    }

    wx.request({
      url: app.globalData.baseUrl + url,
      method: method,
      data: data,
      header: header,
      success: function (res) {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          // 未登录，清除 token
          app.clearAuth()
          reject(new Error('未登录'))
        } else {
          var msg = (res.data && res.data.detail) || '请求失败'
          wx.showToast({ title: msg, icon: 'none' })
          reject(new Error(msg))
        }
      },
      fail: function (err) {
        wx.showToast({ title: '网络错误', icon: 'none' })
        reject(err)
      },
    })
  })
}

module.exports = { request: request }
