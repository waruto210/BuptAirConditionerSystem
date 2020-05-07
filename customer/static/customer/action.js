let timer = 0;
let online = false;
$(document).ready(function() {
    $("#control_btn").on("click", function() {
        if(online === false) {
            online = true;
            get_time();
            timer = setInterval(get_time, 5 * 1000);
        } else {
            online = false;
            clearInterval(timer);
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
