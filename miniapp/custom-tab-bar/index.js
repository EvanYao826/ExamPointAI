// 简笔画 SVG 图标（预编码 base64）
var ICONS = {
  book: {
    normal: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0OCA0OCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjOTk5IiBzdHJva2Utd2lkdGg9IjMiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTYgOGMwLTEgMS0yIDItMmgxMmMyIDAgNCAxIDQgM3YzMGMtMi0xLTQtMi02LTJIOGMtMSAwLTItMS0yLTJWOHoiLz48cGF0aCBkPSJNNDIgOGMwLTEtMS0yLTItMkgyOGMtMiAwLTQgMS00IDN2MzBjMi0xIDQtMiA2LTJoMTBjMSAwIDItMSAyLTJWOHoiLz48L3N2Zz4=',
    active: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0OCA0OCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNEE5MEQ5IiBzdHJva2Utd2lkdGg9IjMiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTYgOGMwLTEgMS0yIDItMmgxMmMyIDAgNCAxIDQgM3YzMGMtMi0xLTQtMi02LTJIOGMtMSAwLTItMS0yLTJWOHoiLz48cGF0aCBkPSJNNDIgOGMwLTEtMS0yLTItMkgyOGMtMiAwLTQgMS00IDN2MzBjMi0xIDQtMiA2LTJoMTBjMSAwIDItMSAyLTJWOHoiLz48L3N2Zz4=',
  },
  person: {
    normal: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0OCA0OCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjOTk5IiBzdHJva2Utd2lkdGg9IjMiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PGNpcmNsZSBjeD0iMjQiIGN5PSIxNCIgcj0iOCIvPjxwYXRoIGQ9Ik04IDQyYzAtOCA3LTE0IDE2LTE0czE2IDYgMTYgMTQiLz48L3N2Zz4=',
    active: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0OCA0OCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNEE5MEQ5IiBzdHJva2Utd2lkdGg9IjMiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PGNpcmNsZSBjeD0iMjQiIGN5PSIxNCIgcj0iOCIvPjxwYXRoIGQ9Ik04IDQyYzAtOCA3LTE0IDE2LTE0czE2IDYgMTYgMTQiLz48L3N2Zz4=',
  },
}

Component({
  data: {
    selected: 0,
    tabs: [
      { path: '/pages/index/index', text: '刷题', icon: ICONS.book },
      { path: '/pages/mine/mine', text: '我的', icon: ICONS.person },
    ],
  },

  methods: {
    switchTab: function (e) {
      var path = e.currentTarget.dataset.path
      var index = e.currentTarget.dataset.index
      this.setData({ selected: index })
      wx.switchTab({ url: path })
    },
  },
})
