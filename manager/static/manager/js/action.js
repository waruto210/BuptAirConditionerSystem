/*
 * @Author: your name
 * @Date: 2020-06-26 21:17:53
 * @LastEditTime: 2020-06-26 23:36:47
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /django-air/manager/static/manager/js/action.js
 */ 




$(document).ready(function() {
    
    $rpt_day_btn = $("#rpt_day");
    $date_from= $("#dpd1");
    $date_to= $("#dpd2");
    console.log(date_from,date_to,'ssssss')
    $rpt_day_btn.on("click", function() {
        date_from = $date_from.val();
        date_to = $date_to.val();
        console.log(date_from,date_to,'ssssss')
        postgetdayrpt(date_from,date_to,'d')
    })
})


function postgetrpt(date_from,date_to,r_type){
    console.log("查询报表");
    $.ajax({
        url: 'get_reports',
        type: 'POST',
        dataType: 'JSON',
        data: {
            'date_from':date_from,
            'date_to':date_to,
            'r_type':r_type
        },
        success: function (ret) {
            console.log(ret)
        }
    })
}
