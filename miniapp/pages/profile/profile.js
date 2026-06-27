var request = require('../../utils/request').request

Page({
  data: {
    // 学校
    schoolName: '',
    // 专业
    majorName: '',
    // 科目
    allSubjects: [],
    selectedSubjects: [],
    subjectInput: '',
    showSubjectDropdown: false,
    filteredSubjects: [],
    // 状态
    submitting: false,
    subjectTapping: false,
  },

  onLoad: function () {
    this.loadSubjects()
    this.loadExistingProfile()
  },

  loadExistingProfile: function () {
    var that = this
    request('/api/v1/user/profile')
      .then(function (res) {
        var data = {}
        if (res.school_name) data.schoolName = res.school_name
        if (res.major_name) data.majorName = res.major_name
        if (Object.keys(data).length > 0) {
          that.setData(data)
        }
      })
      .catch(function () {})
    request('/api/v1/user/subjects')
      .then(function (res) {
        if (res.length > 0) {
          that.setData({ selectedSubjects: res })
        }
      })
      .catch(function () {})
  },

  // ===== 学校输入 =====
  onSchoolInput: function (e) {
    this.setData({ schoolName: e.detail.value })
  },

  // ===== 专业输入 =====
  onMajorInput: function (e) {
    this.setData({ majorName: e.detail.value })
  },

  // ===== 科目选择 =====
  loadSubjects: function () {
    var that = this
    request('/api/v1/subject/list')
      .then(function (res) {
        that.setData({ allSubjects: res, filteredSubjects: res })
      })
      .catch(function () {})
  },

  onSubjectInput: function (e) {
    var keyword = e.detail.value
    this.setData({ subjectInput: keyword })
    if (keyword) {
      var filtered = this.data.allSubjects.filter(function (s) {
        return s.name.indexOf(keyword) >= 0
      })
      this.setData({ filteredSubjects: filtered, showSubjectDropdown: true })
    } else {
      this.setData({ filteredSubjects: this.data.allSubjects, showSubjectDropdown: true })
    }
  },

  onSubjectFocus: function () {
    this.setData({ showSubjectDropdown: true })
  },

  onSubjectBlur: function () {
    var that = this
    setTimeout(function () {
      if (!that.data.subjectTapping) {
        that.setData({ showSubjectDropdown: false })
      }
      that.setData({ subjectTapping: false })
    }, 300)
  },

  onSubjectItemTap: function (e) {
    this.setData({ subjectTapping: true })
    var id = e.currentTarget.dataset.id
    var name = e.currentTarget.dataset.name
    var selected = this.data.selectedSubjects
    for (var i = 0; i < selected.length; i++) {
      if (selected[i].id === id) {
        wx.showToast({ title: '已选择该科目', icon: 'none' })
        return
      }
    }
    selected.push({ id: id, name: name })
    this.setData({
      selectedSubjects: selected,
      subjectInput: '',
      showSubjectDropdown: false,
    })
  },

  addCustomSubject: function () {
    var name = this.data.subjectInput.trim()
    if (!name) {
      wx.showToast({ title: '请输入科目名称', icon: 'none' })
      return
    }
    // 检查是否和已有科目重名
    var all = this.data.allSubjects
    for (var i = 0; i < all.length; i++) {
      if (all[i].name === name) {
        var selected = this.data.selectedSubjects
        for (var j = 0; j < selected.length; j++) {
          if (selected[j].id === all[i].id) {
            wx.showToast({ title: '已选择该科目', icon: 'none' })
            return
          }
        }
        selected.push({ id: all[i].id, name: all[i].name })
        this.setData({ selectedSubjects: selected, subjectInput: '' })
        return
      }
    }
    var selected = this.data.selectedSubjects
    for (var j = 0; j < selected.length; j++) {
      if (selected[j].name === name) {
        wx.showToast({ title: '已选择该科目', icon: 'none' })
        return
      }
    }
    selected.push({ id: 0, name: name })
    this.setData({ selectedSubjects: selected, subjectInput: '' })
  },

  removeSubject: function (e) {
    var index = e.currentTarget.dataset.index
    var selected = this.data.selectedSubjects
    selected.splice(index, 1)
    this.setData({ selectedSubjects: selected })
  },

  // ===== 提交 =====
  submit: function () {
    var schoolName = this.data.schoolName.trim()
    var majorName = this.data.majorName.trim()
    if (!schoolName) {
      wx.showToast({ title: '请输入学校名称', icon: 'none' })
      return
    }
    if (!majorName) {
      wx.showToast({ title: '请输入专业名称', icon: 'none' })
      return
    }
    if (this.data.selectedSubjects.length === 0) {
      wx.showToast({ title: '请至少选择一个科目', icon: 'none' })
      return
    }

    var that = this
    that.setData({ submitting: true })

    request('/api/v1/user/profile', 'PUT', {
      school_name: schoolName,
      major_name: majorName,
    })
      .then(function () {
        var existingIds = []
        var customNames = []
        for (var i = 0; i < that.data.selectedSubjects.length; i++) {
          var s = that.data.selectedSubjects[i]
          if (s.id > 0) {
            existingIds.push(s.id)
          } else {
            customNames.push(s.name)
          }
        }
        return request('/api/v1/user/subjects', 'POST', {
          subject_ids: existingIds,
          subject_names: customNames,
        })
      })
      .then(function () {
        that.setData({ submitting: false })
        wx.showToast({ title: '保存成功', icon: 'success' })
        setTimeout(function () {
          wx.switchTab({ url: '/pages/index/index' })
        }, 1200)
      })
      .catch(function () {
        that.setData({ submitting: false })
      })
  },

  skip: function () {
    wx.switchTab({ url: '/pages/index/index' })
  },
})
