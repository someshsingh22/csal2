from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import redirect, render

from .model import Experience, UserStage


class Calibration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    precision = models.FloatField(null=True, default=None)

    def __str__(self):
        return f"{self.user.username} - {self.precision}"


class CalibrationForm(forms.ModelForm):
    class Meta:
        model = Calibration
        fields = ["user", "precision"]
        widgets = {
            "precision": forms.TextInput(
                attrs={"type": "range", "min": "0", "max": "100"}
            )
        }


@login_required
def CalibrateView(request):
    user = request.user
    stage = UserStage.objects.get(user=user)
    if request.method == "POST":
        form = CalibrationForm(request.POST)
        if form.is_valid():
            form.save()
            if form.fields["precision"] == 0:
                return redirect("/calibrate")
            stage.update()
            return redirect("/")
    else:
        form = CalibrationForm(initial={"user": user})
        return render(request, "form/calib.html", {"form": form})
