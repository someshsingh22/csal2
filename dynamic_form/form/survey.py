from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_control

from .model import Brand, Experience, UserStage


class SurveyQA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand_recog = models.ManyToManyField(Brand, related_name="brand_options")
    mage_id = models.CharField(max_length=100)
    submit_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Survey"


class SurveyQAForm(forms.ModelForm):
    class Meta:
        model = SurveyQA
        fields = ["user", "brand_recog", "mage_id"]
        widgets = {
            "user": forms.HiddenInput(),
            "brand_recog": forms.CheckboxSelectMultiple(),
            "mage_id": forms.TextInput(
                attrs={"placeholder": "https://www.mage.space/u/XXX..."}
            ),
        }
        labels = {
            "mage_id": "Please provide the URL to your Mage Space profile:",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["user"].initial = user
        exp = Experience.objects.get(user=user)
        self.fields["brand_recog"].queryset = exp.brand_recog.all()
        self.fields[
            "brand_recog"
        ].label = (
            "In the eye tracking study, I remember seeing Ads of the following brands:"
        )


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def SurveyFormView(request):
    if SurveyQA.objects.filter(user=request.user).exists():
        return redirect("/experience")
    stage = UserStage.objects.get(user=request.user)
    if request.method == "POST":
        form = SurveyQAForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            stage.update()
            return redirect("/experience")
        else:
            return render(request, "form/survey.html", {"form": form})
    else:
        form = SurveyQAForm(user=request.user)
    return render(request, "form/survey.html", {"form": form})
