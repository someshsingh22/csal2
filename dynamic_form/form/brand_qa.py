import random

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import redirect, render
from multiselectfield import MultiSelectField
from itertools import chain
from django.utils.safestring import mark_safe

from .model import Brand, Experience, UserStage, Video
from .survey import SurveyQA


class BrandQA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    scene_description = models.CharField(max_length=1000)
    audio_types = MultiSelectField(
        choices=[
            (0, "Narration"),
            (1, "Background Music"),
            (2, "Silent"),
            (3, "Don't Remember"),
        ],
        max_choices=3,
        max_length=100,
    )
    prod_usage = models.IntegerField()
    used_before = models.BooleanField()
    submit_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand.name} - Questionnaire"


class BrandQAForm(forms.ModelForm):
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
        ]
        widgets = {
            "user": forms.HiddenInput(),
            "brand": forms.HiddenInput(),
            "audio_types": forms.CheckboxSelectMultiple(),
        }
        labels = {
            "audio_types": "For the {brand} ad(s), What type of audio did you hear? (Select all that apply)",
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

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        brand = cleaned_data.get("brand")
        if BrandQA.objects.filter(user=user, brand=brand).exists():
            self.add_error(
                "user",
                f"You have already completed the questionnaire for {brand.name}",
            )
        audio_types = cleaned_data.get("audio_types")
        if len(audio_types) == 0:
            self.add_error(
                "audio_types", "Please select at least one audio type for the ad(s)"
            )
        


@login_required
def BrandQAView(request, brand_id):
    brand = Brand.objects.get(id=brand_id)
    user = request.user
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
            return render(
                request,
                "form/brand_qa.html",
                {"form": form, "brand": brand, "progress": progress, "total": total},
            )
    else:
        form = BrandQAForm(user=user, brand=brand)

    return render(
        request,
        "form/brand_qa.html",
        {"form": form, "brand": brand, "progress": progress, "total": total},
    )


class BrandDescQA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    video_description_option_out = models.ManyToManyField(Video)
    submit_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand.name} - Description Questionnaire"

class SpecialCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=(), renderer=None):
        output = []
        for index, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            if value is None:
                value = []
            if option_value in value:
                checked = ' checked="checked"'
            else:
                checked = ""
            output.append(
                '<label><input type="checkbox" name="%s" value="%s"%s /> <b>%s</b> %s</label>'
                % (name, option_value, checked, option_label['title'], option_label['description'])
            )
        return mark_safe("".join(output))


class BrandDecQAForm(forms.ModelForm):
    class Meta:
        model = BrandDescQA
        fields = ["user", "brand", "video_description_option_out"]
        widgets = {
            "user": forms.HiddenInput(),
            "brand": forms.HiddenInput(),
            "video_description_option_out": SpecialCheckboxSelectMultiple(),
        }
        labels = {
            "video_description_option_out": "For the {brand} ad(s), Which of the following video descriptions do you remember seeing (Select all that apply)?",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        brand = kwargs.pop("brand")
        super().__init__(*args, **kwargs)
        self.fields["user"].initial = user
        self.fields["brand"].initial = brand
        self.fields["video_description_option_out"].label = self.fields[
            "video_description_option_out"
        ].label.format(brand=brand.name)
        exp = Experience.objects.get(user=user)
        in_videos = Video.objects.filter(brand=brand, experience=exp).all()
        out_videos = (
            Video.objects.filter(brand=brand)
            .exclude(id__in=[video.id for video in in_videos])
        )
        if 5 - len(in_videos) - out_videos.count() > 0:
            out_brand_videos = (
                Video.objects.exclude(brand=brand)
                .order_by("?")[: 5 - len(in_videos) - len(out_videos)]
                .all()
            )
            videos = list(in_videos) + list(out_videos.all()) + list(out_brand_videos)
        else:
            videos = list(in_videos) + list(out_videos.order_by("?")[:5 - len(in_videos)])
        random.shuffle(videos)

        self.fields["video_description_option_out"].choices = [
            (video.id, {"title": video.title, "description": video.desc})
            for video in videos
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        brand = cleaned_data.get("brand")
        if BrandDescQA.objects.filter(user=user, brand=brand).exists():
            self.add_error(
                "user",
                f"You have already completed the questionnaire for {brand.name}",
            )
        return cleaned_data

@login_required
def BrandDescQAView(request, brand_id):
    brand = Brand.objects.get(id=brand_id)
    user = request.user
    userstage = UserStage.objects.get(user=user)
    progress = BrandDescQA.objects.filter(user=user).count() + 1

    if request.method == "POST":
        form = BrandDecQAForm(request.POST, user=user, brand=brand)
        if form.is_valid():
            form.save()
            userstage.update()
            return redirect("/experience")
        else:
            return render(
                request,
                "form/brand_desc.html",
                {"form": form, "brand": brand, "progress": progress, "total": 10},
            )
    else:
        form = BrandDecQAForm(user=user, brand=brand)

    return render(
        request,
        "form/brand_desc.html",
        {"form": form, "brand": brand, "progress": progress, "total": 10},
    )
