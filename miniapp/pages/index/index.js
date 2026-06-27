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

  // 加载科目列表
  loadSubjects: function () {
    var that = this
    request('/api/v1/subject/list')
      .then(function (res) {
        if (res.length > 0) {
          // 读取上次选中的科目，默认第一个
          var savedId = wx.getStorageSync('currentSubjectId')
          var current = res[0]
          for (var i = 0; i < res.length; i++) {
            if (res[i].id === savedId) {
              current = res[i]
              break
            }
          }
          that.setData({ subjects: res, currentSubject: current })
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
  },

  switchTab: function (e) {
    this.setData({ rankingTab: e.currentTarget.dataset.tab })
  },

  goToPublicBank: function () {
    withLogin(function () {
      wx.showToast({ title: '公共题库开发中', icon: 'none' })
    })
  },

  goToMyBank: function () {
    withLogin(function () {
      wx.showToast({ title: '我的题库开发中', icon: 'none' })
    })
  },

  goToWrong: function () {
    withLogin(function () {
      wx.showToast({ title: '错题本开发中', icon: 'none' })
    })
  },

  goToUpload: function () {
    withLogin(function () {
      wx.showToast({ title: '上传题库开发中', icon: 'none' })
    })
  },
})
