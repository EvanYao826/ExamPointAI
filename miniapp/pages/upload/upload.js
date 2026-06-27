var request = require('../../utils/request').request

Page({
  data: {
    tab: 'all',
    tasks: [],
    allTasks: [],
    loading: false,
    pollingTimer: null,
  },

  onLoad: function () {
    this.loadTasks()
  },

  onShow: function () {
    this.loadTasks()
  },

  onUnload: function () {
    if (this.data.pollingTimer) {
      clearInterval(this.data.pollingTimer)
    }
  },

  switchTab: function (e) {
    var tab = e.currentTarget.dataset.tab
    this.setData({ tab: tab })
    this.filterTasks()
  },

  filterTasks: function () {
    var all = this.data.allTasks
    if (this.data.tab === 'done') {
      // 只显示解析成功且有题目的
      var done = all.filter(function (t) {
        return t.status === 2 && t.success_count > 0
      })
      this.setData({ tasks: done })
    } else {
      this.setData({ tasks: all })
    }
  },

  loadTasks: function () {
    var that = this
    that.setData({ loading: true })
    request('/api/v1/upload/tasks')
      .then(function (res) {
        that.setData({ allTasks: res, loading: false })
        that.filterTasks()
        that.checkAndStartPolling(res)
      })
      .catch(function () {
        that.setData({ loading: false })
      })
  },

  checkAndStartPolling: function (tasks) {
    var hasParsing = false
    for (var i = 0; i < tasks.length; i++) {
      if (tasks[i].status === 1) {
        hasParsing = true
        break
      }
    }

    if (hasParsing && !this.data.pollingTimer) {
      this.startPolling()
    } else if (!hasParsing && this.data.pollingTimer) {
      this.stopPolling()
    }
  },

  startPolling: function () {
    var that = this
    var timer = setInterval(function () {
      that.loadTasks()
    }, 3000)
    that.setData({ pollingTimer: timer })
  },

  stopPolling: function () {
    if (this.data.pollingTimer) {
      clearInterval(this.data.pollingTimer)
      this.setData({ pollingTimer: null })
    }
  },

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

  goToBank: function (e) {
    var bankId = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/question/question?bank_id=' + bankId })
  },
})
