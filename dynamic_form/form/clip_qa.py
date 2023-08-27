from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_control

from .model import AudioClip, UserStage


class AudioClipQA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    audio_clip = models.ForeignKey(AudioClip, on_delete=models.CASCADE)
    seen = models.BooleanField(default=False)
    seek_time = models.IntegerField(default=0)
    submit_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand.name} - QA"


class AudioClipQAForm(forms.ModelForm):
    seen = forms.ChoiceField(
        choices=((False, "No"), (True, "Yes")),
        widget=forms.RadioSelect,
        label="Have you heard this audio before?",
    )

    class Meta:
        model = AudioClipQA
        fields = ["user", "audio_clip", "seen", "seek_time"]
        widgets = {
            "user": forms.HiddenInput(),
            "audio_clip": forms.HiddenInput(),
            "seek_time": forms.HiddenInput(),
        }

    def clean_seek_time(self):
        seek_time = self.cleaned_data.get("seek_time")
        if seek_time is not None and seek_time <= 3:
            raise forms.ValidationError("You need to listen to the audio before submitting!")
        return seek_time

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def AudioClipQAView(request, audio_clip_id):
    audio_clip = AudioClip.objects.get(id=audio_clip_id)
    user_stage = UserStage.objects.get(user=request.user)

    if AudioClipQA.objects.filter(user=request.user, audio_clip=audio_clip).exists():
        return redirect("/experience")

    if request.method == "POST":
        form = AudioClipQAForm(request.POST)
        if form.is_valid():
            form.save()
            user_stage.update()
            return redirect("/experience")
        else:
            return render(
                request,
                "form/audio_clip_qa.html",
                {"form": form, "audio_clip": audio_clip.url},
            )

    else:
        form = AudioClipQAForm(initial={"user": request.user, "audio_clip": audio_clip})
        progress = AudioClipQA.objects.filter(user=request.user).count()
        return render(
            request,
            "form/audio_clip_qa.html",
            {"form": form, "audio_clip": audio_clip.url, "progress": progress},
        )
