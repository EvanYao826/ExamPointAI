var request = require('../../utils/request').request
var requireLogin = require('../../utils/auth').requireLogin
var isLoggedIn = require('../../utils/auth').isLoggedIn

Page({
  data: {
    userInfo: {},
    stats: {},
  },

  onShow: function () {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 1 })
    }
    if (isLoggedIn()) {
      this.loadUserInfo()
    } else {
      this.setData({ userInfo: {}, stats: {} })
    }
  },

  // 点击未登录区域触发登录
  onLoginTap: function () {
    var that = this
    requireLogin().then(function () {
      that.loadUserInfo()
    }).catch(function () {})
  },

  // 加载用户信息
  loadUserInfo: function () {
    var that = this
    request('/api/v1/user/profile')
      .then(function (res) {
        var phone = res.phone || ''
        that.setData({
          userInfo: {
            id: res.id,
            nickname: res.nickname || '微信用户',
            avatar: res.avatar || '',
            phone: phone.length === 11 ? phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '',
          },
        })
        that.loadStatistics()
      })
      .catch(function () {})
  },

  // 加载学习统计
  loadStatistics: function () {
    var that = this
    request('/api/v1/statistics/overview')
      .then(function (res) {
        that.setData({
          stats: {
            total_count: res.total_count || 0,
            accuracy: res.total_accuracy ? (res.total_accuracy * 100).toFixed(1) : '0.0',
            continue_days: res.continue_days || 0,
          },
        })
      })
      .catch(function () {})
  },

  goToMyBanks: function () {
    wx.navigateTo({ url: '/pages/bank/bank?tab=mine' })
  },

  goToProfile: function () {
    wx.navigateTo({ url: '/pages/profile/profile' })
  },

  goToSettings: function () {
    wx.navigateTo({ url: '/pages/settings/settings' })
  },
})
