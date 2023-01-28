import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .model import Experience, UserStage, Video
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
            message = "Please watch the videos to continue."
            link = "/experience"
            link_text = "Videos"
        elif stage.stage == 17:
            message = "Please answer this question to continue."
            link = "/consistency_check"
            link_text = "Question"
        elif stage.stage == 18:
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
        elif stage.stage == 19:
            message = "Please answer the questions to continue."
            link = "/survey"
            link_text = "survey"
        else:
            brands = SurveyQA.objects.get(user=user).brand_recog.all()
            if stage.stage < 50:
                if stage.stage - 20 >= len(brands):
                    stage.update()
                    stage.stage = 50
                    stage.save()
                    return redirect("/")
                else:
                    brand = brands[stage.stage - 20]
                    return redirect("/brand/" + str(brand.id))
            else:
                if stage.stage < 70:
                    scenes = Experience.objects.get(user=user).scene_seen.all()
                    scene = scenes[stage.stage - 50].id
                    return redirect("/scene/" + str(scene))
                else:
                    brands = [
                        v.brand for v in Experience.objects.get(user=user).videos.all()
                    ]
                    if stage.stage - 70 >= len(brands):
                        message = "Thank you for your participation!"
                        link = "/accounts/logout"
                        link_text = "Logout"
                    else:
                        brand = brands[stage.stage - 70]
                        return redirect("/desc/" + str(brand.id))
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
    extra_video = 16

    if stage in video_stages:
        video = videos[video_stages.index(stage)]
        return redirect(f"/video/{video.id}/{gaze}?extra=False")
    elif stage in popup_stages:
        start, end = STAGE_SLICES[popup_stages.index(stage)]
        return redirect(f"/popup/{start},{end}")
    elif stage == extra_video:
        uid = request.user.id
        if uid % 2 == 0:
            video_id = (
                Video.objects.exclude(
                    id__in=Experience.objects.get(user=request.user).videos.all()
                )
                .order_by("?")[0]
                .id
            )
        else:
            video_id = Experience.objects.get(user=request.user).videos.all()[uid].id
        return redirect(f"/video/{video_id}/0?extra=True")
    else:
        print("Invalid stage, redirecting to home, stage: ", stage)
        return redirect("/")
