Page({
  data: {
    currentSubject: '操作系统',
    rankingTab: 'daily',
    medals: ['🥇', '🥈', '🥉'],
    rankingList: [
      { rank: 1, nickname: '张三', count: 128 },
      { rank: 2, nickname: '李四', count: 117 },
      { rank: 3, nickname: '王五', count: 106 },
    ],
    myRank: 8,
    myCount: 52,
  },

  onLoad() {
    // 检查登录状态
    const app = getApp()
    if (!app.globalData.token) {
      wx.redirectTo({ url: '/pages/login/login' })
      return
    }
    // TODO: 加载真实数据
  },

  // 切换排行榜 Tab
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({ rankingTab: tab })
    // TODO: 加载对应排行榜数据
  },

  // 进入公共题库
  goToBank() {
    // TODO: 跳转题库列表页
    wx.showToast({ title: '题库列表开发中', icon: 'none' })
  },
})
