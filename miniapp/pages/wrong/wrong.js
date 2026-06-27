var request = require('../../utils/request').request

Page({
  data: {
    bankList: [],
    totalCount: 0,
    loading: false,
  },

  onLoad: function () {
    this.loadData()
  },

  onShow: function () {
    this.loadData()
  },

  loadData: function () {
    var that = this
    that.setData({ loading: true })

    Promise.all([
      request('/api/v1/wrong/by-bank'),
      request('/api/v1/wrong/count'),
    ])
      .then(function (results) {
        that.setData({
          bankList: results[0],
          totalCount: results[1].count,
          loading: false,
        })
      })
      .catch(function () {
        that.setData({ loading: false })
      })
  },

  // 进入错题重做
  goRedo: function (e) {
    var bankId = e.currentTarget.dataset.id
    var bankName = e.currentTarget.dataset.name
    wx.navigateTo({
      url: '/pages/question/question?bank_id=' + bankId + '&bank_name=' + encodeURIComponent(bankName) + '&mode=wrong',
    })
  },
})
