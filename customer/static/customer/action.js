let timer = 0;
let online = false;
let ws = null;
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