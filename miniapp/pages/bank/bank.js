var request = require('../../utils/request').request

Page({
  data: {
    tab: 'public',
    banks: [],
    loading: false,
    keyword: '',
  },

  onLoad: function (options) {
    if (options.tab === 'mine') {
      this.setData({ tab: 'mine' })
    }
  },

  onShow: function () {
    this.loadBanks()
  },

  switchTab: function (e) {
    this.setData({ tab: e.currentTarget.dataset.tab, keyword: '' })
    this.loadBanks()
  },

  onSearch: function (e) {
    this.setData({ keyword: e.detail.value })
    this.loadBanks()
  },

  loadBanks: function () {
    var that = this
    var baseUrl = this.data.tab === 'public' ? '/api/v1/bank/public' : '/api/v1/bank/mine'
    var subjectId = wx.getStorageSync('currentSubjectId')
    var url = baseUrl + (subjectId ? '?subject_id=' + subjectId : '')

    that.setData({ loading: true })

    request(url)
      .then(function (res) {
        var filtered = res
        if (that.data.keyword) {
          var kw = that.data.keyword.toLowerCase()
          filtered = res.filter(function (b) {
            return b.name.toLowerCase().indexOf(kw) !== -1
          })
        }
        that.setData({ banks: filtered, loading: false })
      })
      .catch(function () {
        that.setData({ loading: false })
      })
  },

  goToQuestion: function (e) {
    var id = e.currentTarget.dataset.id
    var name = e.currentTarget.dataset.name
    wx.navigateTo({
      url: '/pages/question/question?bank_id=' + id + '&bank_name=' + encodeURIComponent(name),
    })
  },

  // 跳转添加题库页
  onUpload: function () {
    wx.navigateTo({ url: '/pages/upload/upload' })
  },
})
