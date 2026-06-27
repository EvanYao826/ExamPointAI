var request = require('../../utils/request').request

// 状态映射
var STATUS = {
  0: '已上传',
  1: '解析中',
  2: '解析成功',
  3: '解析失败',
}

Page({
  data: {
    tab: 'all',
    tasks: [],
    loading: false,
  },

  onLoad: function () {
    this.loadTasks()
  },

  onShow: function () {
    this.loadTasks()
  },

  switchTab: function (e) {
    this.setData({ tab: e.currentTarget.dataset.tab })
    this.loadTasks()
  },

  loadTasks: function () {
    var that = this
    that.setData({ loading: true })

    var url = '/api/v1/upload/tasks'
    if (that.data.tab === 'done') {
      url += '?status=0'
    }

    request(url)
      .then(function (res) {
        that.setData({ tasks: res, loading: false })
      })
      .catch(function () {
        that.setData({ loading: false })
      })
  },

  // 上传题库
  onUpload: function () {
    var that = this
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      extension: ['.doc', '.docx', '.pdf'],
      success: function (res) {
        var file = res.tempFiles[0]
        if (file.size > 20 * 1024 * 1024) {
          wx.showToast({ title: '文件不能超过20MB', icon: 'none' })
          return
        }
        that.uploadFile(file)
      },
    })
  },

  uploadFile: function (file) {
    var that = this
    var subjectId = wx.getStorageSync('currentSubjectId') || 1

    wx.showLoading({ title: '上传中...', mask: true })

    wx.uploadFile({
      url: getApp().globalData.baseUrl + '/api/v1/upload/file',
      filePath: file.path,
      name: 'file',
      formData: {
        subject_id: String(subjectId),
        bank_name: file.name.replace(/\.(doc|docx|pdf)$/i, ''),
      },
      header: {
        'Authorization': 'Bearer ' + getApp().globalData.token,
      },
      success: function (res) {
        wx.hideLoading()
        if (res.statusCode === 200) {
          wx.showToast({ title: '上传成功', icon: 'success' })
          that.loadTasks()
        } else {
          var msg = '上传失败'
          try { msg = JSON.parse(res.data).detail || msg } catch (e) {}
          wx.showToast({ title: msg, icon: 'none' })
        }
      },
      fail: function () {
        wx.hideLoading()
        wx.showToast({ title: '上传失败', icon: 'none' })
      },
    })
  },
})
