document.addEventListener("fullscreenchange", exitHandler, false);
document.addEventListener("mozfullscreenchange", exitHandler, false);
document.addEventListener("webkitfullscreenchange", exitHandler, false);
document.addEventListener("msfullscreenchange", exitHandler, false);
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
const correctAnswers = {
    "I am paid bi-weekly by leprechauns": "Disagree",
    "In the last one year, I have suffered from congenital parantoscopy": "0 times",
    "I know that people have to pay brands to advertise brand’s products": "Agree",
    "I have never used a computer": "Disagree",
    "What is 5+7?": "12",
    "What is 6*9": "54",
    "The Apple brand which manufactures iPhones is a sub-brand of the Google and Facebook brands": "Disagree",
    "How many times have you written the gospel of ghost and the demon in this course this year?": "Never",
    "The founders of brands Apple, Google, Facebook, PayTM, Maruti, Dell, and Toyota are of Pakistani origin:": "Disagree",
    "All brands congregate at the North Pole on the New Year’s eve and stop their advertising for one day:": "Disagree",
    "If I could, I would want to pass this course:": "Agree",
    "What is 6+7?": "13",
    "What is 4*9": "36",
    "How many legs does a cow have?": "4",
    "How many prime ministers India has had in the last 70 years?": "15",
    "How many states do we have in India?": "28",
    "How many oceans are there in the world?": "5",
    "What is the closest expected average age of your undergrad class?": "20 years",
    "What is the closest expected average lifetime of an Indian?": "60 years",
    "What is the closest Indian Rupees to United States Dollar Exchange rate?": "80 rupee = 1 dollar",
    "Which of these is a geographical neighbor of India?": "Pakistan",
    "USA stands for United States of India?": "False",
    "CNG stands for Compressed Non-natural Genome?": "False",
    "On Earth, the Sun rises in the East and sets in the west?": "True",
    "Moon is bigger than Earth in size?": "False",
    "Sun is bigger than the Earth’s Moon?": "True",
    "How many hours do we have in a day?": "24",
    "The maximum percentage a student has ever scored in CBSE physics board exams is:": "100%",
    "The river Ganga flows from?": "Himalayas to the Indian Ocean",
    "If I puncture 2 tyres of my car at the same time, how many mechanics do I need to repair them?": "1",
    "What is the volume of 10 litres of petrol?": "10 L",
    "If my car travels 50 kms North on a road and then 50 kms South on the same road, how much distance has my car travelled?": "100 kms",
    "A humming bird and an eagle have a competition, who will win?": "Hummingbird or Eagle",
    "IIIT-Delhi and IIT-Delhi have a competition, who will win?": "IIIT-Delhi or IIT-Delhi",
};

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

function req_fs(){
    if (video.requestFullscreen) {
        video.requestFullscreen();
    }
    else if (video.mozRequestFullScreen) {
        video.mozRequestFullScreen();
    }
    else if (video.webkitEnterFullscreen) {
        video.webkitEnterFullscreen();
    }
    else if (video.webkitRequestFullScreen) {
        video.webkitRequestFullScreen();
    }
    else if (video.msRequestFullscreen) {
        video.msRequestFullscreen();
    }
    else {
        alert("Your browser doesn't support fullscreen mode");
    }
}

function cancel_fs(){
    if (video.exitFullscreen) {
        video.exitFullscreen();
    }
    else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
    }
    else if (video.webkitExitFullScreen) {
        video.webkitExitFullScreen();
    }
    else if (video.msExitFullscreen) {
        video.msExitFullscreen();
    }
}


function play(timer, gaze) {
    if (gaze == 1) webgazer_init();
    req_fs();
    video.play();
    setTimeout(function() {
        check_form.hidden = false;
        play_div.hidden = true;
        flag = true;
        video.pause();
        cancel_fs();
        curr_time = Math.floor(Date.now() / 1000);
    }, timer);
}

function sequel(time_limit) {
    const selectedAnswer = document.querySelector('input[name="check"]:checked').value;
    const question = document.querySelector('label').textContent;
    var time = Math.floor(Date.now() / 1000);
    if (selectedAnswer !== correctAnswers[question]) {
        alert("Incorrect answer");
        location.reload();
    }
    else if (time - curr_time > time_limit) {
        alert("Too slow, please watch again!");
        location.reload();
    }
    check_form.hidden = true;
    play_div.hidden = false;
    flag = false;
    req_fs();
    video.play();
}

video.onended = function() {
    if (typeof webgazer !== 'undefined') webgazer.pause();
    flag = true;
    cancel_fs();
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
    cancel_fs();
    alert("You can't exit the video, please watch again!");
    location.reload();
}
}

video.addEventListener('click', function() {
flag = true;
video.pause();
cancel_fs();
alert("You can't pause the video, please watch again!");
location.reload();
});