import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .model import Experience, UserStage
from .survey import SurveyQA

WAIT_TIME = datetime.timedelta(seconds=10)


def home_view(request):
    if request.user.is_authenticated:
        user = request.user
        stage = UserStage.objects.get(user=user)
        gaze = Experience.objects.get(user=user).gaze
        if stage.stage == 1:
            message = "Please fill this short form to continue."
            link = "/intro"
            link_text = "Introduction"
        if stage.stage == 2:
            if gaze == 0:
                stage.update()
                return redirect("/")
            else:
                message = "Please calibrate your eye tracker to continue."
                link = "/calib"
                link_text = "Calibration"
        elif stage.stage >= 3 and stage.stage <= 15:
            message = "Please watch the videos to continue."
            link = "/experience"
            link_text = "Videos"
        elif stage.stage == 16:
            time_elapsed = timezone.now() - stage.last_updated
            time_remaining = (WAIT_TIME - time_elapsed).total_seconds()
            if time_remaining > 0:
                hours = int(time_remaining // 3600)
                minutes = int((time_remaining % 3600) // 60)
                seconds = int(time_remaining % 60)
                read_time = ""
                if hours > 0:
                    read_time += f"{hours} hours "
                if minutes > 0:
                    read_time += f"{minutes} minutes "
                if seconds > 0:
                    read_time += f"{seconds} seconds "
                message = "Stay Tuned! You can logout for now your next action item will be available in {}".format(
                    read_time
                )
                link = "/accounts/logout"
                link_text = "Logout"
            else:
                stage.update()
                return redirect("/")
        elif stage.stage == 17:
            message = "Please answer the questions to continue."
            link = "/survey"
            link_text = "survey"
        elif stage.stage >= 18 and stage.stage < 38:
            return redirect("/experience")
        elif stage.stage >= 38:
            brands = SurveyQA.objects.get(user=user).brand_recog.all()
            if stage.stage - 38 >= len(brands):
                message = "Thank you for your participation!"
                link = "/accounts/logout"
                link_text = "Logout"
            else:
                return redirect("/experience")
        return render(
            request,
            "home.html",
            {"message": message, "link": link, "link_text": link_text},
        )
    else:
        return redirect("accounts/login/")


@login_required
def experience_view(request):
    user = request.user
    user_stage = UserStage.objects.get(user=user)
    experience = Experience.objects.get(user=user)
    stage, gaze = user_stage.stage, experience.gaze
    videos = experience.videos.all()
    scenes = experience.scene_seen.all()

    STAGE_SLICES = [
        (0, 3),
        (3, 6),
        (6, 10),
    ]
    video_stages = [3, 4, 5, 7, 8, 9, 11, 12, 13, 14]
    popup_stages = [6, 10, 15]
    scene_stages = list(range(18, 38))

    if stage in video_stages:
        video = videos[video_stages.index(stage)]
        return redirect(f"/video/{video.id}/{gaze}")
    elif stage in popup_stages:
        start, end = STAGE_SLICES[popup_stages.index(stage)]
        return redirect(f"/popup/{start},{end}")
    elif stage < scene_stages[0]:
        return redirect(f"/")
    elif stage in scene_stages:
        scene_idx = stage - scene_stages[0]
        scene = scenes[scene_idx]
        return redirect(f"/scene/{scene.id}")
    else:
        brands = SurveyQA.objects.get(user=user).brand_recog.all()
        if stage - (scene_stages[-1] + 1) >= len(brands):
            return redirect("/")
        else:
            brand = brands[stage - (scene_stages[-1] + 1)]
            return redirect(f"/brand/{brand.id}")
