import random

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import redirect, render
from multiselectfield import MultiSelectField

from .model import Brand, Experience, UserStage, Video
from .survey import SurveyQA


class BrandQA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    scene_description = models.CharField(max_length=1000)
    audio_types = models.CharField(max_length=100)
    prod_usage = models.IntegerField()
    used_before = models.BooleanField()
    submit_duration = models.IntegerField(default=0)
    scene_options_out = MultiSelectField(
        choices=[(0, "SD1"), (1, "SD2"), (2, "SD3"), (3, "SD4"), (4, "SD5")],
        max_choices=5,
        max_length=1000,
    )
    scene_options_in = models.CharField(max_length=1000, default="")

    def __str__(self):
        return f"{self.brand.name} - Questionnaire"


class BrandQAForm(forms.ModelForm):
    audio_types = forms.ChoiceField(
        choices=[
            ("narration", "Narration"),
            ("background_music", "Background Music"),
            ("both", "Both"),
            ("no_music", "No Music"),
            ("dont_remember", "Don't Remember"),
        ],
        widget=forms.RadioSelect,
        label="For the {brand} ad(s), I remember hearing the following audio types:",
    )
    prod_usage = forms.ChoiceField(
        choices=[
            (0, "0"),
            (1, "1-10"),
            (2, "10+"),
        ],
        widget=forms.RadioSelect,
        label="How many times in the last 1 year have you used the product shown in the {brand} ad(s)?",
    )
    used_before = forms.ChoiceField(
        choices=[
            (True, "Yes"),
            (False, "No"),
        ],
        widget=forms.RadioSelect,
        label="Have you ever used {brand} before?",
    )
    scene_description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        label="For the {brand} ad(s), I remember seeing the following (Write Scene Descriptions, feel free to write any scenes, music,characters,emotions,objects you remember seeing)",
    )

    class Meta:
        model = BrandQA
        fields = [
            "user",
            "brand",
            "scene_description",
            "audio_types",
            "prod_usage",
            "used_before",
            "submit_duration",
            "scene_options_out",
            "scene_options_in",
        ]
        widgets = {
            "user": forms.HiddenInput(),
            "brand": forms.HiddenInput(),
            "submit_duration": forms.HiddenInput(),
            "scene_options_out": forms.CheckboxSelectMultiple(),
            "scene_options_in": forms.HiddenInput(),
        }
        labels = {
            "scene_options_out": "For the {brand} ad(s), Which of the following scenes do you remember seeing (Select all that apply)?",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        brand = kwargs.pop("brand")
        super().__init__(*args, **kwargs)
        self.fields["user"].initial = user
        self.fields["brand"].initial = brand
        self.fields["audio_types"].label = self.fields["audio_types"].label.format(
            brand=brand.name
        )
        self.fields["prod_usage"].label = self.fields["prod_usage"].label.format(
            brand=brand.name
        )
        self.fields["used_before"].label = self.fields["used_before"].label.format(
            brand=brand.name
        )
        self.fields["scene_description"].label = self.fields[
            "scene_description"
        ].label.format(brand=brand.name)
        self.fields["scene_options_out"].label = self.fields[
            "scene_options_out"
        ].label.format(brand=brand.name)


@login_required
def BrandQAView(request, brand_id):
    brand = Brand.objects.get(id=brand_id)
    user = request.user
    exp = Experience.objects.get(user=user)
    in_videos = list(Video.objects.filter(id__in=exp.videos.all(), brand=brand))
    out_videos = list(
        Video.objects.exclude(id__in=exp.videos.all()).filter(brand=brand)
    )
    if len(out_videos) + len(in_videos) < 5:
        out_brand_videos = list(
            Video.objects.exclude(id__in=exp.videos.all()).exclude(brand=brand)
        )
        videos = (
            in_videos
            + out_videos
            + random.sample(out_brand_videos, 5 - len(in_videos) - len(out_videos))
        )
    else:
        videos = in_videos + random.sample(out_videos, 5 - len(in_videos))
    random.shuffle(videos)
    descriptions = [v.desc for v in videos]

    userstage = UserStage.objects.get(user=user)
    total = SurveyQA.objects.get(user=user).brand_recog.count()
    progress = BrandQA.objects.filter(user=user).count() + 1
    if request.method == "POST":
        form = BrandQAForm(request.POST, user=user, brand=brand)
        if form.is_valid():
            form.save()
            userstage.update()
            return redirect("/experience")
    else:
        form = BrandQAForm(user=user, brand=brand)
        form.fields["scene_options_out"].choices = [
            (i, descriptions[i]) for i in range(len(descriptions))
        ]
        form.fields["scene_options_in"].initial = ",".join([str(v.id) for v in videos])

    return render(
        request,
        "form/brand_qa.html",
        {"form": form, "brand": brand, "progress": progress, "total": total},
    )
