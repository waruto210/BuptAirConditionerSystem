let ws = null;

let POWER_ON = "power_on", POWER_OFF = "power_off", CHANGE_SP = "change_sp", CHANGE_MODE = "change_mode", CHANGE_GOAL = "change_goal";
let HEART_BEAT = "heaer_beat";

let total_high_time = 0, total_mid_time = 0, total_low_time = 0;

let cost_low = 1 / 3, cost_mid = 1 / 2, cost_high = 1;
let temp_low = 2, temp_mid = 2, temp_high = 2;
// 关机时每分钟变化
let temp_off = 2;
// 上一次计算费用，温度变化的时间
let last_cost_time = 0;

let rate_timer = null;
// 轮询定时器
let timer = null;
// 机器是否在工作(调度)
let is_work = false;
// 用户是否开机
let power_on = false;
// 目标温度,环境温度
let goal_temp;
let curr_temp;
let env_temp;
// 工作模式,0为制冷
let work_mode = 0;
// 风速模式
let sp_mode = 1;
// 总费用
let total_cost = 0;

let room_id = "200";
// 目标温度上下限
let hot_sub = 25, hot_sup = 30;
let cold_sub = 18, cold_sup = 25;

$(document).ready(function() {
    // 获取默认环境温度
    env_temp = parseInt($("#curr_temp").text());
    curr_temp = env_temp;
    goal_temp = parseInt($("#goal_temp").text());


    $("#power_btn").on("click", function() {     
        if(power_on === false) {
            power_on = true;
            post_power()
        } else {
            power_on = false;
            is_work = false;
        }
        if( power_on == true ) {
            last_cost_time = Date.parse(new Date()) / 1000;
            // console.log('time:', last_cost_time);
            timer = setInterval(poll, 5*1000);
        } else {
            clearInterval(timer);
            clear_rate();
            curr_temp = env_temp;
        }   
    });

    $("#mode_btn").on("click", function(){
        let img = $("#pic_mode").attr("src");
        console.log(img)
        let tmp = img.split('/')
        
        if(tmp[tmp.length - 1] === "snow.png"){
            if (goal_temp < hot_sub) {
                alert("目标温度过低，无法切换模式");
            } else {
                tmp[tmp.length - 1] = "sun.png"
                $("#pic_mode").attr("src", tmp.join("/"));
                work_mode = 1;
            }
            // console.log(document.getElementById("pic_mode").src);
        } else {
            if(goal_temp > cold_sup) {
                alert("目标温度过高，无法切换模式");
            } else {
                tmp[tmp.length - 1] = "snow.png"
                $("#pic_mode").attr("src", tmp.join("/"));
                work_mode = 0;
            }
            // console.log(document.getElementById("pic_mode").src);
        }
        post_poll(CHANGE_MODE);
    });

    $("#temp_add_btn").on("click", function() {
        goal_temp = parseInt($("#goal_temp").text()) + 1;
        if(work_mode == 1 && goal_temp > hot_sup) {
            goal_temp = hot_sup;
            alert("已经达到制热模式最大温度");
        } else if(work_mode== 0 && goal_temp > cold_sup) {
            alert("已经达到制冷模式最大温度，请切换到制热模式");
            goal_temp = cold_sup;
        } else {
            $("#goal_temp").text(goal_temp);
        }
        post_poll(CHANGE_GOAL);
    });

    $("#temp_minus_btn").on("click", function() {
        goal_temp = parseInt($("#goal_temp").text()) - 1;
        if(work_mode==0 && goal_temp < cold_sub) {
            goal_temp = cold_sub;
            alert("已经达到制冷模式最低温度");
        } else if(work_mode==1 && goal_temp == cold_sup) {
            goal_temp = hot_sub;
            alert("已经达到制热模式最低温度，请切换到制冷模式");
        } else {
            $("#goal_temp").text(goal_temp);
        }
        post_poll(CHANGE_GOAL);
    });


    $("#spd_btn").on("click", function() {
        if(sp_mode == 0){
            $("#speed").text("中风");
            cal_cost();
            sp_mode++;
            clearInterval(rate_timer);
            
            temp_low = temp_mid;
        }else if(sp_mode == 1){
            $("#speed").text("高风");
            cal_cost();
            sp_mode++;
            rate_timer = setInterval(change_rate, 10*1000);
        } else {
            $("#speed").text("低风");
            cal_cost();
            sp_mode = 0;
            clearInterval(rate_timer);
            rate_timer = setInterval(change_rate, 10*1000);
            temp_high = temp_mid;
        }
        post_poll(CHANGE_SP);
    });
});


function change_rate() {
    
    if(sp_mode == 0) {
        temp_low *= 0.8;
        console.log("change_rate to:", temp_low);
    } else if(sp_mode == 2){
        temp_high *= 1.2;
        console.log("change_rate to:", temp_high);
    }
}

function clear_rate() {
    clearInterval(rate_timer);
    temp_low = temp_mid;
    temp_high = temp_mid;
}


function cal_cost() {
    now_time = Date.parse(new Date()) / 1000;
    gap = now_time - last_cost_time;
    if(is_work == true) {
        // 计算温度变化
        new_temp = 0;
        if(sp_mode == 0) {
            total_cost += (gap / 60) * cost_low;
            if(goal_temp > curr_temp) {
                new_temp = Math.min(curr_temp + (gap / 60) * temp_low, goal_temp);
            } else {
                new_temp = Math.max(curr_temp - (gap / 60) * temp_low, goal_temp);
            }
        } else if(sp_mode == 1) {
            total_cost += (gap / 60) * cost_mid;
            if(goal_temp > curr_temp) {
                new_temp = Math.min(curr_temp + (gap / 60) * temp_mid, goal_temp);
            } else {
                new_temp = Math.max(curr_temp - (gap / 60) * temp_mid, goal_temp);
            }
        } else {
            total_cost += (gap / 60) * cost_high;
            if(goal_temp > curr_temp) {
                new_temp = Math.min(curr_temp + (gap / 60) * temp_high, goal_temp);
            } else {
                new_temp = Math.max(curr_temp - (gap / 60) * temp_high, goal_temp);
            }
        }
        $("#total_cost").text(total_cost.toFixed(2));
        curr_temp = new_temp;
        $("#curr_temp").text(curr_temp.toFixed(2));
        
    } else {
        new_temp = 0;
        if(curr_temp > env_temp) {
            new_temp = Math.max(curr_temp - (gap / 60) * temp_off, env_temp);
        } else {
            new_temp = Math.min(curr_temp + (gap / 60) * temp_off, env_temp);
        }
        if (curr_temp != new_temp) {
            curr_temp = new_temp;
            $("#curr_temp").text(curr_temp.toFixed(2));
        }
    }
    last_cost_time = now_time;
}


function poll() {
    cal_cost();
    ins = HEART_BEAT;
    post_poll(ins);
}
function post_poll(ins) {
    obj = {
        'url': 'poll',
        'data': {
            'room_id': room_id,
            'ins': ins,
            'goal_temp': goal_temp,
            'curr_temp': curr_temp,
            'sp_mode': sp_mode,
            'work_mode': work_mode,
            'total_cost': total_cost,
        },
    }
    myajax(obj, function(data) {
        is_work = data.is_work
        console.log(data)
        if(is_work == false) {
            clear_rate();
        }
    })
}
function post_power() {
    obj = {
        'url': 'poweron',
        'data': {
            'room_id': room_id,
            'ins': POWER_ON,
            'goal_temp': goal_temp,
            'curr_temp': curr_temp,
            'sp_mode': sp_mode,
            'work_mode': work_mode,
            'total_cost': total_cost,
        },
    }
    myajax(obj, function(data) {
        is_work = data.is_work
        if(is_work == false) {
            clear_rate();
            $("#air_state").text("中央主机暂未送风");
        } else {
            $("#air_state").text("空调工作中");
        }
    })
}


myajax = function(obj, successFn){
    $.ajax({
        url: obj.url,
        data: obj.data,
        dataType: 'json',
        type: 'POST',
        success: function(data){
            if (data.code != 200) {
                alert(data.msg);
            } else {
                successFn(data.data)
            }
        },
        error: function(err){
            alert(err)
        }
    })
}



function openws() {
    ws = new WebSocket('ws://' + window.location.host + '/ws/tuisong/');

    ws.onopen = function(evt) { 
      console.log("Connection open ..."); 
    };
    
    ws.onmessage = function(evt) {
        var data = JSON.parse(evt.data)['msg'];
      console.log( "Received Message: " + data);
    };
    
    ws.onclose = function(evt) {
      console.log("Connection closed.");
    };
}
function closews() {
    ws.close();
    ws = null;
}

window.onbeforeunload = function () {
    ws.close()
    console.log(1);//在刷新页面或者关闭页面需要断开websocket
};


