var withLogin = require('../../utils/auth').withLogin

Page({
  data: {
    currentSubject: '操作系统',
    rankingTab: 'daily',
    medals: ['🥇', '🥈', '🥉'],
    rankingList: [],
    myRank: 0,
    myCount: 0,
  },

  onShow: function () {
    // 设置 tabBar 选中态
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 0 })
    }
  },

  // 切换排行榜 Tab
  switchTab: function (e) {
    this.setData({ rankingTab: e.currentTarget.dataset.tab })
  },

  // 公共题库（需登录）
  goToPublicBank: function () {
    withLogin(function () {
      wx.showToast({ title: '公共题库开发中', icon: 'none' })
    })
  },

  // 我的题库（需登录）
  goToMyBank: function () {
    withLogin(function () {
      wx.showToast({ title: '我的题库开发中', icon: 'none' })
    })
  },

  // 错题本（需登录）
  goToWrong: function () {
    withLogin(function () {
      wx.showToast({ title: '错题本开发中', icon: 'none' })
    })
  },

  // 上传题库（需登录）
  goToUpload: function () {
    withLogin(function () {
      wx.showToast({ title: '上传题库开发中', icon: 'none' })
    })
  },
})
