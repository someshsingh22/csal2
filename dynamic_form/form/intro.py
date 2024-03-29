from django import forms
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import cache_control
from multiselectfield import MultiSelectField

from .model import Brand, Experience, UserStage


class Introduction(models.Model):
    age = models.IntegerField()
    gender = models.CharField(max_length=1)
    stream = models.CharField(max_length=100)
    experience = models.OneToOneField(Experience, on_delete=models.CASCADE)
    brands_seen = models.ManyToManyField(Brand, related_name="intro_brands_seen")
    prod_used = models.ManyToManyField(Brand, related_name="intro_prod_used")
    ad_block = models.BooleanField()
    youtube_sub = models.BooleanField()
    youtube_mobile = models.IntegerField()
    apprise = MultiSelectField(
        choices=[
            ("1", "Primarily friends and family"),
            ("2", "Amazon, Flipkart or any other e-commerce stores"),
            (
                "3",
                "Television and OTT Platform Ads (like Youtube, Netflix, Hotstar, etc)",
            ),
            ("4", "Email Ads"),
            ("5", "Store Visits"),
            ("6", "Website Ads"),
            ("7", "I primarily search for products"),
        ],
        max_choices=7,
        max_length=100,
    )
    submit_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}_Introduction"


class IntroductionForm(forms.ModelForm):
    age = forms.IntegerField(label="What is your age?", min_value=15, max_value=35, widget=forms.NumberInput(attrs={'placeholder': 'Enter your age'}))
    gender = forms.ChoiceField(
        choices=(
            ('M', "Male"),
            ('F', "Female"),
            ('O', "Other"),
        ),
        label="What is your gender?",
        widget=forms.RadioSelect(),
    )
    #stream, They can select from ['ECE', 'CSB', 'CSE', 'CSAI', 'CSD', 'CSAM', 'CSSS', "other"] 
    stream = forms.ChoiceField(
        choices=(
            ('ECE', "ECE"),
            ('CSB', "CSB"),
            ('CSE', "CSE"),
            ('CSAI', "CSAI"),
            ('CSD', "CSD"),
            ('CSAM', "CSAM"),
            ('CSSS', "CSSS"),
            ('OTHER', "Other")
        ),
        label="What is your stream?",
        widget=forms.RadioSelect(),
    )
    ad_block = forms.ChoiceField(
        choices=((False, "No"), (True, "Yes")),
        widget=forms.RadioSelect,
        label="Do you use an ad blocking software?",
    )
    youtube_sub = forms.ChoiceField(
        choices=((False, "No"), (True, "Yes")),
        widget=forms.RadioSelect,
        label="Do you use a Youtube subscription?",
    )
    youtube_mobile = forms.ChoiceField(
        choices=(
            (1, "<10% on mobile"),
            (2, ">10% but <30% on mobile"),
            (3, ">30% but <70% on mobile"),
            (4, ">70% on mobile"),
        ),
        widget=forms.RadioSelect,
        label="Approximately how much percentage of time do you spend on Youtube mobile vs Youtube web?",
    )

    class Meta:
        model = Introduction
        fields = [
            "experience",
            "age",
            "gender",
            "stream",
            "brands_seen",
            "prod_used",
            "ad_block",
            "youtube_sub",
            "youtube_mobile",
            "apprise",
        ]
        widgets = {
            "experience": forms.HiddenInput(),
            "brands_seen": forms.CheckboxSelectMultiple(),
            "prod_used": forms.CheckboxSelectMultiple(),
            "apprise": forms.CheckboxSelectMultiple(),
        }
        labels = {
            "brands_seen": "I remember seeing ads for the following brands this year:",
            "prod_used": "I remember using products of the following brands this year:",
            "apprise": "How do you apprise yourself of the latest products and brands? (Multi correct)",
        }


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def IntroView(request):
    user = request.user
    exp = Experience.objects.get(user=user)
    stage = UserStage.objects.get(user=user)

    if Introduction.objects.filter(experience=exp).exists():
        return redirect("/")

    if request.method == "POST":
        form = IntroductionForm(request.POST)
        if form.is_valid():
            form.save()
            stage.stage = max(2, stage.stage)
            stage.save()
            exp.start_time = timezone.now()
            return redirect("/")
        else:
            print(form.errors)
            return render(request, "form/intro.html", {"form": form})
    else:
        if stage.stage > 1:
            return redirect("/")
        exp = Experience.objects.get(user=request.user)
        form = IntroductionForm(initial={"experience": exp})
        brand_seen_options = exp.brands_seen_options.all()
        prod_used_options = exp.prod_used_options.all()
        form.fields["brands_seen"].queryset = brand_seen_options
        form.fields["prod_used"].queryset = prod_used_options
    return render(request, "form/intro.html", {"form": form})
