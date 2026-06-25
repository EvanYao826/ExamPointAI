const { request } = require('../../utils/request')

Page({
  data: {
    phone: '',
    code: '',
    countdown: 0,
  },

  // 手机号输入
  onPhoneInput(e) {
    this.setData({ phone: e.detail.value })
  },

  // 验证码输入
  onCodeInput(e) {
    this.setData({ code: e.detail.value })
  },

  // 发送验证码
  onSendCode() {
    const { phone } = this.data
    if (phone.length !== 11) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }

    request('/api/v1/auth/sms/send', 'POST', { phone })
      .then(() => {
        wx.showToast({ title: '验证码已发送', icon: 'success' })
        this.startCountdown()
      })
      .catch(() => {})
  },

  // 倒计时
  startCountdown() {
    this.setData({ countdown: 60 })
    const timer = setInterval(() => {
      const { countdown } = this.data
      if (countdown <= 1) {
        clearInterval(timer)
        this.setData({ countdown: 0 })
      } else {
        this.setData({ countdown: countdown - 1 })
      }
    }, 1000)
  },

  // 登录
  onLogin() {
    const { phone, code } = this.data
    if (phone.length !== 11 || code.length !== 6) {
      wx.showToast({ title: '请填写完整信息', icon: 'none' })
      return
    }

    wx.showLoading({ title: '登录中...' })

    request('/api/v1/auth/sms/login', 'POST', { phone, code })
      .then((res) => {
        const app = getApp()
        app.setToken(res.access_token)

        wx.hideLoading()
        wx.showToast({ title: '登录成功', icon: 'success' })

        // 跳转首页
        setTimeout(() => {
          wx.switchTab({ url: '/pages/index/index' })
        }, 1000)
      })
      .catch(() => {
        wx.hideLoading()
      })
  },
})
