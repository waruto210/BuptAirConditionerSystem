let timer = 0;
let online = false;
let ws = null;
let goal_temp;
let sp_mode = 0;
let total_cost = 0;

$(document).ready(function() {
    $("#control_btn").on("click", function() {
        if(online === false) {
            online = true;
            get_time();
            openws();
            timer = setInterval(get_time, 5 * 1000);
        } else {
            online = false;
            clearInterval(timer);
            closews();
            $("#timer").text("停止了");
        }
    });

    $("#mode_btn").on("click", function() {
        let img = document.getElementById("pic_mode").src;
        let tmp = img.split('/')
        
        if(tmp[tmp.length - 1] === "snow.png"){
            tmp[tmp.length - 1] = "sun.png"
            $("#pic_mode").attr("src", tmp.join("/"));
            // console.log(document.getElementById("pic_mode").src);
        }else {
            tmp[tmp.length - 1] = "snow.png"
            $("#pic_mode").attr("src", tmp.join("/"));
            // console.log(document.getElementById("pic_mode").src);
        }
    });

    $("#temp_add_btn").on("click", function() {
        goal_temp = parseInt(document.getElementById("temp").innerText)+1;
        document.getElementById("temp").innerHTML = goal_temp;
    });

    $("#temp_minus_btn").on("click", function() {
        goal_temp = document.getElementById("temp").innerText -1;
        document.getElementById("temp").innerHTML = goal_temp;
    });


    $("#spd_btn").on("click", function() {
        if(sp_mode==0){
            $("#speed").text("中风");
            sp_mode++;
        }else if(sp_mode==1){
            $("#speed").text("高风");
            sp_mode++;
        }else {
            $("#speed").text("低风");
            sp_mode=0;
        }
        
    });
});


function get_time() {
    jQuery.ajax({
		type:'GET',
		url:'get_time',
		dataType:'json',
		success:function(data){
            console.log(data.time)
            $("#timer").text(data.time);
        }
    });
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