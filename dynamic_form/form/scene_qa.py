from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import redirect, render

from .model import UserStage, VideoScene


class SceneQA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scene = models.ForeignKey(VideoScene, on_delete=models.CASCADE)
    seen = models.BooleanField(default=False)
    submit_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand.name} - QA"


class ScenesQAForm(forms.ModelForm):
    seen = forms.ChoiceField(
        choices=((False, "No"), (True, "Yes")),
        widget=forms.RadioSelect,
        label="Have you seen this scene before?",
    )

    class Meta:
        model = SceneQA
        fields = ["user", "scene", "seen"]
        widgets = {
            "user": forms.HiddenInput(),
            "scene": forms.HiddenInput(),
        }


@login_required
def SceneQAView(request, scene_id):
    scene = VideoScene.objects.get(id=scene_id)
    user_stage = UserStage.objects.get(user=request.user)
    if request.method == "POST":
        form = ScenesQAForm(request.POST)
        if form.is_valid():
            form.save()
            user_stage.update()
            return redirect("/experience")
        else:
            return render(
                request,
                "form/scene_qa.html",
                {"form": form, "scene": scene.url},
            )

    else:
        form = ScenesQAForm(initial={"user": request.user, "scene": scene})
        progress = SceneQA.objects.filter(user=request.user).count()
        return render(
            request,
            "form/scene_qa.html",
            {"form": form, "scene": scene.url, "progress": progress},
        )
