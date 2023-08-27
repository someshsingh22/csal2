import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .model import Experience, UserStage, Video
from .survey import SurveyQA

WAIT_TIME = datetime.timedelta(milliseconds=10000)
DESC_FLAG = True


def home_view(request):
    if request.user.is_authenticated:
        user = request.user
        stage = UserStage.objects.get(user=user)
        gaze = Experience.objects.get(user=user).gaze

        if stage.stage == 1:
            message = "Please fill this short form to continue."
            link = "/intro"
            link_text = "Introduction"
        elif stage.stage == 2:
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
            link_text = "Survey"
        elif stage.stage >= 20 and stage.stage <= 90:
            message = "Please answer the questions to continue."
            link = "/experience"
            link_text = "Survey"
        else:
            if DESC_FLAG:
                brands = list(
                    [
                        v.brand
                        for v in Experience.objects.get(user=user).videos.all()
                        if v.brand
                    ]
                )
                unique_brands = []
                for brand in brands:
                    if brand not in unique_brands:
                        unique_brands.append(brand)
                brands = unique_brands
                if stage.stage - 90 >= len(brands):
                    message = "Thank you for your participation!"
                    link = "/accounts/logout"
                    link_text = "Logout"
                else:
                    redirect("/experience")

            else:
                message = "Thank you for your participation!"
                link = "/accounts/logout"
                link_text = "Logout"
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
        video_id = experience.cc_v
        return redirect(f"/video/{video_id}/0?extra=True")
    elif stage == 17:
        return redirect("/consistency_check")
    elif stage == 18:
        return redirect("/")
    elif stage == 19:
        return redirect("/")
    elif stage >= 20 and stage < 50:
        brands = SurveyQA.objects.get(user=user).brand_recog.all()
        if user_stage.stage < 50:
            if user_stage.stage - 20 >= len(brands):
                user_stage.update()
                user_stage.stage = 50
                user_stage.save()
                return redirect("/")
            else:
                brand = brands[user_stage.stage - 20]
                return redirect("/brand/" + str(brand.id))
    elif stage >= 50 and stage < 70:
        scenes = Experience.objects.get(user=user).scene_seen.all()
        try:
            scene = scenes[user_stage.stage - 50].id
        except:
            if user_stage.stage > 65:
                user_stage.update()
                user_stage.stage = 70
                user_stage.save()
                return redirect("/")
            else:
                scene = scenes[user_stage.stage - 50].id
        return redirect("/scene/" + str(scene))
    elif stage >= 70 and stage < 90:
        audios = Experience.objects.get(user=user).audio_seen.all()
        audio_id = audios[user_stage.stage - 70].id
        return redirect("/audio/" + str(audio_id))

    elif stage >= 90:
        if DESC_FLAG:
            brands = list(
                [
                    v.brand
                    for v in Experience.objects.get(user=user).videos.all()
                    if v.brand
                ]
            )
            unique_brands = []
            for brand in brands:
                if brand not in unique_brands:
                    unique_brands.append(brand)
            brands = unique_brands

            if user_stage.stage - 90 >= len(brands):
                return redirect("/")
            else:
                brand = brands[user_stage.stage - 90]
                return redirect("/desc/" + str(brand.id))
        else:
            return redirect("/")
    else:
        return redirect("/")
