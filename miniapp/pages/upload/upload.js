var request = require('../../utils/request').request

Page({
  data: {
    tab: 'all',
    tasks: [],
    allTasks: [],
    loading: false,
    pollingTimer: null,
    currentSubject: '',
    currentSubjectId: 0,
    menuIndex: -1,
  },

  onLoad: function () {
    this.loadCurrentSubject()
    this.loadTasks()
  },

  onShow: function () {
    this.loadCurrentSubject()
    this.loadTasks()
  },

  onUnload: function () {
    if (this.data.pollingTimer) {
      clearInterval(this.data.pollingTimer)
    }
  },

  // 加载当前科目
  loadCurrentSubject: function () {
    var subjectId = wx.getStorageSync('currentSubjectId')
    var subjectName = wx.getStorageSync('currentSubjectName') || '未选择'
    this.setData({ currentSubjectId: subjectId, currentSubject: subjectName })
  },

  // 切换科目
  changeSubject: function () {
    var that = this
    request('/api/v1/user/subjects')
      .then(function (res) {
        if (res.length === 0) {
          wx.showToast({ title: '请先选择科目', icon: 'none' })
          return
        }
        var names = res.map(function (s) { return s.name })
        wx.showActionSheet({
          itemList: names,
          success: function (e) {
            var subject = res[e.tapIndex]
            wx.setStorageSync('currentSubjectId', subject.id)
            wx.setStorageSync('currentSubjectName', subject.name)
            that.setData({ currentSubjectId: subject.id, currentSubject: subject.name })
          },
        })
      })
      .catch(function () {})
  },

  switchTab: function (e) {
    var tab = e.currentTarget.dataset.tab
    this.setData({ tab: tab })
    this.filterTasks()
  },

  filterTasks: function () {
    var all = this.data.allTasks
    if (this.data.tab === 'done') {
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

  // ===== 菜单操作 =====
  toggleMenu: function (e) {
    var index = e.currentTarget.dataset.index
    this.setData({ menuIndex: this.data.menuIndex === index ? -1 : index })
  },

  closeMenu: function () {
    this.setData({ menuIndex: -1 })
  },

  noop: function () {},

  // 重命名
  onRename: function (e) {
    var that = this
    var id = e.currentTarget.dataset.id
    var oldName = e.currentTarget.dataset.name
    that.setData({ menuIndex: -1 })

    wx.showModal({
      title: '重命名',
      editable: true,
      placeholderText: '请输入新名称',
      content: oldName,
      success: function (res) {
        if (res.confirm && res.content && res.content.trim()) {
          var newName = res.content.trim()
          request('/api/v1/upload/task/' + id + '/rename', 'PUT', { name: newName })
            .then(function () {
              wx.showToast({ title: '重命名成功', icon: 'success' })
              that.loadTasks()
            })
            .catch(function () {})
        }
      },
    })
  },

  // 置顶
  onPinTop: function (e) {
    var that = this
    var id = e.currentTarget.dataset.id
    that.setData({ menuIndex: -1 })

    request('/api/v1/upload/task/' + id + '/pin', 'PUT')
      .then(function () {
        wx.showToast({ title: '已置顶', icon: 'success' })
        that.loadTasks()
      })
      .catch(function () {})
  },

  // 删除
  onDelete: function (e) {
    var that = this
    var id = e.currentTarget.dataset.id
    that.setData({ menuIndex: -1 })

    wx.showModal({
      title: '确认删除',
      content: '删除后不可恢复，确定删除吗？',
      success: function (res) {
        if (res.confirm) {
          request('/api/v1/upload/task/' + id, 'DELETE')
            .then(function () {
              wx.showToast({ title: '已删除', icon: 'success' })
              that.loadTasks()
            })
            .catch(function () {})
        }
      },
    })
  },

  // 上传
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
    var subjectId = that.data.currentSubjectId || wx.getStorageSync('currentSubjectId') || 1

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
