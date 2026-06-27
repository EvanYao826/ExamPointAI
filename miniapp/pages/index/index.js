var request = require('../../utils/request').request
var withLogin = require('../../utils/auth').withLogin

Page({
  data: {
    subjects: [],
    currentSubject: {},
    showPicker: false,
    rankingTab: 'daily',
    medals: ['🥇', '🥈', '🥉'],
    rankingList: [],
    myRank: 0,
    myCount: 0,
  },

  onLoad: function () {
    this.loadSubjects()
  },

  onShow: function () {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 0 })
    }
  },

  // 加载科目列表（优先用户已选科目，未登录则加载全部）
  loadSubjects: function () {
    var that = this
    var url = getApp().globalData.token ? '/api/v1/user/subjects' : '/api/v1/subject/list'
    request(url)
      .then(function (res) {
        if (res.length > 0) {
          var savedId = wx.getStorageSync('currentSubjectId')
          var current = res[0]
          for (var i = 0; i < res.length; i++) {
            if (res[i].id === savedId) {
              current = res[i]
              break
            }
          }
          that.setData({ subjects: res, currentSubject: current })
          wx.setStorageSync('currentSubjectId', current.id)
          wx.setStorageSync('currentSubjectName', current.name)
        }
      })
      .catch(function () {})
  },

  // 展开/收起科目选择器
  toggleSubjectPicker: function () {
    this.setData({ showPicker: !this.data.showPicker })
  },

  // 关闭科目选择器
  closePicker: function () {
    this.setData({ showPicker: false })
  },

  // 选择科目
  selectSubject: function (e) {
    var id = e.currentTarget.dataset.id
    var name = e.currentTarget.dataset.name
    this.setData({
      currentSubject: { id: id, name: name },
      showPicker: false,
    })
    wx.setStorageSync('currentSubjectId', id)
    wx.setStorageSync('currentSubjectName', name)
  },

  switchTab: function (e) {
    this.setData({ rankingTab: e.currentTarget.dataset.tab })
  },

  goToPublicBank: function () {
    withLogin(function () {
      wx.navigateTo({ url: '/pages/bank/bank?tab=public' })
    })
  },

  goToMyBank: function () {
    withLogin(function () {
      wx.navigateTo({ url: '/pages/bank/bank?tab=mine' })
    })
  },

  goToWrong: function () {
    withLogin(function () {
      wx.navigateTo({ url: '/pages/wrong/wrong' })
    })
  },

  goToUpload: function () {
    withLogin(function () {
      wx.navigateTo({ url: '/pages/upload/upload' })
    })
  },
})
