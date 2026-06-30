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
    totalCount: 0,
    totalAccuracy: '0.0',
    continueDays: 0,
  },

  onLoad: function () {
    this.loadSubjects()
  },

  onShow: function () {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 0 })
    }
    // 切回首页时刷新排行和统计
    if (this.data.currentSubject.id) {
      this.loadRanking()
      this.loadStatistics()
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
          that.loadRanking()
          that.loadStatistics()
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
    this.loadRanking()
    this.loadStatistics()
  },

  switchTab: function (e) {
    var tab = e.currentTarget.dataset.tab
    this.setData({ rankingTab: tab })
    this.loadRanking()
  },

  // 加载学习统计
  loadStatistics: function () {
    var that = this
    request('/api/v1/statistics/overview')
      .then(function (res) {
        that.setData({
          totalCount: res.total_count || 0,
          totalAccuracy: res.total_accuracy ? (res.total_accuracy * 100).toFixed(1) : '0.0',
          continueDays: res.continue_days || 0,
        })
      })
      .catch(function () {})
  },

  // 加载排行榜
  loadRanking: function () {
    var that = this
    var tab = that.data.rankingTab
    var url = '/api/v1/ranking/' + tab
    request(url)
      .then(function (res) {
        that.setData({
          rankingList: res.list || [],
          myRank: res.my_rank || 0,
          myCount: res.my_total_count || 0,
        })
      })
      .catch(function () {})
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
