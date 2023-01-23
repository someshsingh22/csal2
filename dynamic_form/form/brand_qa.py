from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import redirect, render

from .model import Brand, UserStage


class BrandQA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    audio_types = models.CharField(max_length=100)
    prod_usage = models.IntegerField()
    used_before = models.BooleanField()

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
        label="For the {brand} ad, I remember hearing the following audio types:",
    )
    prod_usage = forms.ChoiceField(
        choices=[
            (0, "0"),
            (1, "1-10"),
            (2, "10+"),
        ],
        widget=forms.RadioSelect,
        label="How many times in the last 1 year have you used the product shown in the {brand} ad?",
    )
    used_before = forms.ChoiceField(
        choices=[
            (True, "Yes"),
            (False, "No"),
        ],
        widget=forms.RadioSelect,
        label="Have you ever used {brand} before?",
    )

    class Meta:
        model = BrandQA
        fields = ["user", "brand", "audio_types", "prod_usage", "used_before"]
        widgets = {
            "user": forms.HiddenInput(),
            "brand": forms.HiddenInput(),
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


@login_required
def BrandQAView(request, brand_id):
    brand = Brand.objects.get(id=brand_id)
    userstage = UserStage.objects.get(user=request.user)
    if request.method == "POST":
        form = BrandQAForm(request.POST, user=request.user, brand=brand)
        if form.is_valid():
            form.save()
            userstage.update()
            return redirect("/experience")
    else:
        form = BrandQAForm(user=request.user, brand=brand)
    return render(request, "form/brand_qa.html", {"form": form, "brand": brand})
