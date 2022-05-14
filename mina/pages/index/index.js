//login.js
//获取应用实例
var app = getApp();
Page({
    data: {
        remind: '加载中',
        angle: 0,
        userInfo: {},
        regFlag: true
    },
    goToIndex: function () {
        wx.switchTab({
            url: '/pages/food/index',
        });
    },
    onLoad: function () {
        wx.setNavigationBarTitle({
            title: app.globalData.shopName
        });
        this.checkLogin();
    },
    onShow: function () {

    },
    onReady: function () {
        var that = this;
        setTimeout(function () {
            that.setData({
                remind: ''
            });
        }, 1000);
        wx.onAccelerometerChange(function (res) {
            var angle = -(res.x * 30).toFixed(1);
            if (angle > 14) {
                angle = 14;
            } else if (angle < -14) {
                angle = -14;
            }
            if (that.data.angle !== angle) {
                that.setData({
                    angle: angle
                });
            }
        });
    },
    checkLogin: function () {
        var that = this;
        wx.login({
            success: function (res) {
                if (!res.code) {
                    app.alert({
                        'content': '登录失败，请再次点击'
                    });
                    return;
                }
                wx.request({
                    url: app.buildUrl('/member/check-reg'),
                    header: app.getRequestHeader(),
                    method: 'POST',
                    data: {
                        code: res.code
                    },
                    success: function (res) {
                        if (res.data.code != 200) {
                            that.setData({
                                regFlag: false
                            });
                            return;
                        }
                        app.setCache("token", res.data.data.token);
                    }
                });
            }
        });
    },
    login: function (e) {
        var that = this;
        wx.getUserProfile({
            desc: "用于更好的展示。",
            fail: function (res) {
                console.log('获取用户信息失败', res)
                wx.showToast({
                    title: '信息授权失败~',
                    duration: 1000,
                    icon: 'error',
                    mask: true
                })
            },
            success: function (res) {
                var data = res.userInfo;
                wx.login({
                    success: function (res) {
                        if (!res.code) {
                            app.alert({
                                'content': '登录失败，请再次点击2~'
                            });
                            return;
                        }
                        data['code'] = res.code;
                        wx.request({
                            url: app.buildUrl('/member/login'),
                            header: app.getRequestHeader(),
                            method: 'POST',
                            data: data,
                            success: function (result) {
                                if (result.data.code != 200) {
                                    app.alert({
                                        'content': result.data.msg
                                    });
                                    return;
                                }
                                app.setCache("token", result.data.data.token);
                                that.goToIndex();
                            }
                        });
                    }
                })
            }
        })
    }
});