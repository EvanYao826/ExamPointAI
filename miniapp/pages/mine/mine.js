var request = require('../../utils/request').request

Page({
  data: {
    userInfo: {},
    stats: {},
  },

  onShow() {
    // 设置 tabBar 选中态
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 1 })
    }
    this.loadUserInfo()
  },

  loadUserInfo: function () {
    var that = this
    request('/api/v1/user/profile')
      .then(function (res) {
        var phone = res.phone || ''
        that.setData({
          userInfo: {
            nickname: res.nickname || '未登录',
            avatar: res.avatar || '',
            phone: phone.length === 11 ? phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '',
          },
        })
      })
      .catch(function () {
        that.setData({ userInfo: { nickname: '未登录', phone: '' } })
      })
  },

  goToMyBanks: function () {
    wx.showToast({ title: '开发中', icon: 'none' })
  },

  goToSubjects: function () {
    wx.showToast({ title: '开发中', icon: 'none' })
  },

  goToSchool: function () {
    wx.showToast({ title: '开发中', icon: 'none' })
  },
})
