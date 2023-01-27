document.addEventListener('fullscreenchange', exitHandler, false);
var curr_time = 0;
var flag = false;
var check_form = document.getElementById("check");
var gaze_form = document.getElementById("gaze");
var play_div = document.getElementById("play");
var gaze_input_x = document.getElementById("gaze_input_x");
var gaze_input_y = document.getElementById("gaze_input_y");
var video = document.getElementById("video");
var x = ""
var y = ""

function webgazer_init() {
    webgazer.setGazeListener(function(data, elapsedTime) {
    if (data == null) {
    return;
    }
    var xprediction = data.x + ",";
    var yprediction = data.y + ",";
    if (video.paused) {
        xprediction = "";
        yprediction = "";
    }
    x+=xprediction
    y+=yprediction
    }).begin();
    webgazer.showVideo(false);
}

function play(timer, gaze) {
    if (gaze == 1) webgazer_init();
    video.requestFullscreen();
    video.play();
    setTimeout(function() {
        check_form.hidden = false;
        play_div.hidden = true;
        flag = true;
        video.pause();
        video.webkitExitFullscreen();
        curr_time = Math.floor(Date.now() / 1000);
    }, timer);
}

function sequel(time_limit) {
    var time = Math.floor(Date.now() / 1000);
    if (time - curr_time > time_limit) {
        alert("Too slow, please watch again!");
        location.reload();
    }
    check_form.hidden = true;
    play_div.hidden = false;
    flag = false;
    video.requestFullscreen();
    video.play();
}

video.onended = function() {
    if (typeof webgazer !== 'undefined') webgazer.pause();
    flag = true;
    video.webkitExitFullscreen();
    gaze_form.hidden = false;
    play_div.hidden = true;
    gaze_input_x.value = x;
    gaze_input_y.value = y;
    console.log(x);
    console.log(y);
};

function exitHandler(){
if (!document.fullscreenElement && !flag){
    video.pause();
    video.webkitExitFullscreen();
    alert("You can't exit the video, please watch again!");
    location.reload();
}
}
video.addEventListener('click', function() {
flag = true;
video.pause();
video.webkitExitFullscreen();
alert("You can't pause the video, please watch again!");
location.reload();
});