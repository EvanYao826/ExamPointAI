var request = require('../../utils/request').request

var TYPE_MAP = {
  single_choice: '单选题',
  multiple_choice: '多选题',
  judge: '判断题',
  fill_blank: '填空题',
  short_answer: '简答题',
}

Page({
  data: {
    bankId: 0,
    bankName: '',
    questions: [],
    currentIndex: 0,
    answers: {},
    multiSelected: {},
    multiCount: 0,
    loading: true,
    showAnalysis: false,
    typeText: '',
    difficultyStars: '',
    // 预处理的选项状态
    optionStates: [], // [{ key, content, isCorrect, isWrong }]
  },

  onLoad: function (options) {
    this.setData({
      bankId: options.bank_id,
      bankName: decodeURIComponent(options.bank_name || '刷题'),
    })
    if (options.question_id) {
      this.loadSingleQuestion(options.question_id)
    } else if (options.mode === 'wrong') {
      this.loadWrongQuestions()
    } else {
      this.loadAllQuestions()
    }
  },

  // 加载错题
  loadWrongQuestions: function () {
    var that = this
    that.setData({ loading: true })
    request('/api/v1/wrong/questions?bank_id=' + that.data.bankId)
      .then(function (res) {
        if (res.length === 0) {
          that.setData({ loading: false, questions: [] })
          return
        }
        that.setData({ questions: res, loading: false })
        that.showQuestion(0)
      })
      .catch(function () {
        that.setData({ loading: false })
      })
  },

  loadAllQuestions: function () {
    var that = this
    that.setData({ loading: true })
    request('/api/v1/bank/' + that.data.bankId + '/questions')
      .then(function (res) {
        if (res.length === 0) {
          that.setData({ loading: false, questions: [] })
          return
        }
        that.setData({ questions: res, loading: false })
        that.showQuestion(0)
      })
      .catch(function () {
        that.setData({ loading: false })
      })
  },

  loadSingleQuestion: function (questionId) {
    var that = this
    that.setData({ loading: true })
    request('/api/v1/question/' + questionId + '/analysis')
      .then(function (res) {
        that.setData({ questions: [res], loading: false })
        that.showQuestion(0)
      })
      .catch(function () {
        that.setData({ loading: false })
      })
  },

  getStars: function (n) {
    var s = ''
    for (var i = 0; i < n; i++) s += '⭐'
    return s
  },

  // 显示指定题目
  showQuestion: function (idx) {
    var q = this.data.questions[idx]
    var answer = this.data.answers[q.id]
    var optionStates = this.buildOptionStates(q.options, answer)

    this.setData({
      currentIndex: idx,
      typeText: TYPE_MAP[q.type] || q.type,
      difficultyStars: this.getStars(q.difficulty),
      showAnalysis: false,
      multiSelected: {},
      multiCount: 0,
      optionStates: optionStates,
    })
  },

  // 预处理选项状态
  buildOptionStates: function (options, answer) {
    var correctMap = {}
    var selectedMap = {}

    if (answer) {
      // 把 "ABC" 拆成 {A:true, B:true, C:true}
      for (var i = 0; i < answer.correctAnswer.length; i++) {
        correctMap[answer.correctAnswer[i]] = true
      }
      for (var j = 0; j < answer.selected.length; j++) {
        selectedMap[answer.selected[j]] = true
      }
    }

    var states = []
    for (var k = 0; k < options.length; k++) {
      var opt = options[k]
      states.push({
        key: opt.option_key,
        content: opt.content,
        isCorrect: !!correctMap[opt.option_key],
        isWrong: !!selectedMap[opt.option_key] && !correctMap[opt.option_key],
      })
    }
    return states
  },

  getCurrentQuestion: function () {
    return this.data.questions[this.data.currentIndex]
  },

  getCurrentAnswer: function () {
    var q = this.getCurrentQuestion()
    return q ? this.data.answers[q.id] : null
  },

  isMulti: function () {
    var q = this.getCurrentQuestion()
    return q && q.type === 'multiple_choice'
  },

  // 选择选项
  selectOption: function (e) {
    if (this.getCurrentAnswer()) return
    var key = e.currentTarget.dataset.key

    // 多选题
    if (this.isMulti()) {
      var map = this.data.multiSelected
      var count = this.data.multiCount
      if (map[key]) {
        delete map[key]
        count--
      } else {
        map[key] = true
        count++
      }
      this.setData({ multiSelected: map, multiCount: count })
      // 更新选项高亮
      this.updateMultiHighlight()
      return
    }

    // 单选/判断
    this.submitAnswer(key)
  },

  // 多选题实时高亮
  updateMultiHighlight: function () {
    var q = this.getCurrentQuestion()
    var options = q.options
    var selected = this.data.multiSelected
    var states = []
    for (var i = 0; i < options.length; i++) {
      var opt = options[i]
      states.push({
        key: opt.option_key,
        content: opt.content,
        isCorrect: false,
        isWrong: false,
        isMultiSelected: !!selected[opt.option_key],
      })
    }
    this.setData({ optionStates: states })
  },

  // 提交答案
  submitAnswer: function (userAnswer) {
    var that = this
    var question = that.getCurrentQuestion()

    request('/api/v1/question/submit', 'POST', {
      question_id: question.id,
      user_answer: userAnswer,
      cost_time: 0,
    })
      .then(function (res) {
        var answers = that.data.answers
        answers[question.id] = {
          selected: userAnswer,
          isCorrect: res.is_correct,
          correctAnswer: res.correct_answer,
          analysis: res.analysis,
        }
        that.setData({ answers: answers, multiSelected: {}, multiCount: 0 })
        // 重新构建选项状态
        that.setData({
          optionStates: that.buildOptionStates(question.options, answers[question.id]),
        })
      })
      .catch(function () {})
  },

  // 多选题提交
  submitMulti: function () {
    var map = this.data.multiSelected
    var keys = Object.keys(map).sort()
    if (keys.length === 0) {
      wx.showToast({ title: '请至少选择一项', icon: 'none' })
      return
    }
    this.submitAnswer(keys.join(''))
  },

  toggleAnalysis: function () {
    this.setData({ showAnalysis: !this.data.showAnalysis })
  },

  switchQuestion: function (e) {
    var idx = typeof e === 'number' ? e : e.currentTarget.dataset.index
    this.showQuestion(idx)
  },

  prevQuestion: function () {
    var idx = this.data.currentIndex
    if (idx <= 0) {
      wx.showToast({ title: '已经是第一题', icon: 'none' })
      return
    }
    this.showQuestion(idx - 1)
  },

  nextQuestion: function () {
    var idx = this.data.currentIndex
    if (idx >= this.data.questions.length - 1) {
      wx.showToast({ title: '已经是最后一题', icon: 'none' })
      return
    }
    this.showQuestion(idx + 1)
  },

  goBack: function () {
    wx.navigateBack()
  },
})
