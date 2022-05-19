;
var finance_index_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        var that = this;
        $(".wrap_search select[name=status]").change(function () {
            $(".wrap_search").submit();
        });
    }
};

$(document).ready(function () {
    finance_index_ops.init();
});
// window.onload=function () {
//     document.getElementById('countdown').click();
// }
//
// function countDown(time) {
//     // + new Date();返回的是当前时间总的毫秒数
//     var nowTime = +new Date();
//     var inTime = +new Date(time)//返回的是用户输入时间总的毫秒数
//     var secondTime = (inTime - nowTime) / 1000;//剩余时间总的秒数
//     var d = parseInt(secondTime / 60 / 60 / 24);//计算天数
//     d = d < 10 ? '0' + d : d;//当天数小于10时补0
//     var h = parseInt(secondTime / 60 / 60 % 24);//计算小时
//     h = h < 10 ? '0' + h : h;
//     var m = parseInt(secondTime / 60 % 60);  //计算分
//     m = m < 10 ? '0' + m : m;
//     var s = parseInt(secondTime % 60);       //计算当前秒数
//     s = s < 10 ? '0' + s : s;
//     time1 = d + '天' + h + '时' + m + '分';
//     countdown = document.getElementById('countdown');
//     countdown.innerHTML = time1;
// }
