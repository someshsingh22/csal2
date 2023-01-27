from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import redirect, render

from .model import Brand, Experience, UserStage, Video

NUMERIC_MAPPING = {
    0: "1st",
    1: "2nd",
    2: "3rd",
    3: "4th",
    4: "5th",
    5: "6th",
    6: "7th",
    7: "8th",
    8: "9th",
    9: "10th",
}


class Popup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    seen_before = models.BooleanField()
    seen_brand_before = models.BooleanField()
    heard_before = models.BooleanField()
    clear_product = models.BooleanField()
    submit_duration = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.video.name}"


class PopupSliceForm(forms.Form):
    seen_before = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Have you seen these exact ads before?",
    )
    seen_brand_before = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Have you seen any ads from these brands before?",
    )
    heard_before = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Have you heard of these brands prior to this study?",
    )
    clear_product = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="For the previously seen ad(s) Check if the product being advertised is clear",
    )
    submit_duration = forms.IntegerField(
        widget=forms.HiddenInput(), initial=0, required=False
    )

    def __init__(self, videos, *args, **kwargs):
        super().__init__(*args, **kwargs)
        video_brands = Brand.objects.filter(video__in=videos).distinct()

        club_options = {video.brand: "" for video in videos}
        for i, video in enumerate(videos):
            club_options[video.brand] += f"{NUMERIC_MAPPING[i]}, "

        for key, value in club_options.items():
            club_options[key] = f"{key.name} ({value[:-2]})"

        self.fields["seen_before"].choices = [
            (video.id, f"{NUMERIC_MAPPING[index]} ({video.brand.name})")
            for index, video in enumerate(videos)
        ]
        self.fields["seen_brand_before"].choices = [
            (
                brand.id,
                club_options[brand],
            )
            for brand in video_brands
        ]
        self.fields["heard_before"].choices = [
            (
                brand.id,
                club_options[brand],
            )
            for brand in video_brands
        ]
        self.fields["clear_product"].choices = [
            (video.id, f"{NUMERIC_MAPPING[index]} ({video.brand.name})")
            for index, video in enumerate(videos)
        ]


@login_required
def popup_slice(request, start, end):
    user = request.user
    exp = Experience.objects.get(user=user)
    videos = Video.objects.filter(experience=exp).all()
    videos = videos[start:end]
    form = PopupSliceForm(videos)
    user_stage = UserStage.objects.get(user=user)

    if request.method == "POST":
        form = PopupSliceForm(videos, request.POST)
        if form.is_valid():
            for idx in range(end - start):
                video = videos[idx]
                popup = Popup(
                    user=user,
                    video=video,
                    seen_before=video.id in form.cleaned_data["seen_before"],
                    seen_brand_before=video.brand.id
                    in form.cleaned_data["seen_brand_before"],
                    heard_before=video.brand.id in form.cleaned_data["heard_before"],
                    clear_product=video.id in form.cleaned_data["clear_product"],
                    submit_duration=form.cleaned_data["submit_duration"],
                )
                popup.save()
            user_stage.update()
            return redirect("/experience")

        else:
            print(form.errors)
            return render(
                request,
                "form/popup.html",
                {"form": form, "progress": [6, 10, 15].index(user_stage.stage) + 1},
            )

    return render(
        request,
        "form/popup.html",
        {"form": form, "progress": [6, 10, 15].index(user_stage.stage) + 1},
    )
