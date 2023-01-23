import random

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import redirect, render

from .model import Experience, UserStage, Video

MIN_TIMER = 500
TIME_LIMIT = 5000


class AttentionCheckField(forms.Form):
    questions = [
        "I am paid bi-weekly by leprechauns",
        "In the last one year, I have suffered from congenital parantoscopy",
        "I know that people have to pay brands to advertise brand’s products",
        "I have never used a computer",
        "What is 5+7?",
        "What is 6*9",
        "The Apple brand which manufactures iPhones is a sub-brand of the Google and Facebook brands",
        "How many times have you written the gospel of ghost and the demon in this course this year?",
        "The founders of brands Apple, Google, Facebook, PayTM, Maruti, Dell, and Toyota are of Pakistani origin:",
        "All brands congregate at the North Pole on the New Year’s eve and stop their advertising for one day:",
        "If I could, I would want to pass this course:",
        "What is 6+7?",
        "What is 4*9",
        "How many legs does a cow have?",
        "How many prime ministers India has had in the last 70 years?",
        "How many states do we have in India?",
        "How many oceans are there in the world?",
        "What is the closest expected average age of your undergrad class?",
        "What is the closest expected average lifetime of an Indian?",
        "What is the closest Indian Rupees to United States Dollar Exchange rate?"
        "Which of these is a geographical neighbor of India?",
        "USA stands for United States of India?",
        "CNG stands for Compressed Non-natural Genome?",
        "On Earth, the Sun rises in the East and sets in the west?",
        "Moon is bigger than Earth in size?",
        "Sun is bigger than the Earth’s Moon?",
        "How many hours do we have in a day?",
        "The maximum percentage a student has ever scored in CBSE physics board exams is:",
        "The river Ganga flows from?",
        "If I puncture 2 tyres of my car at the same time, how many mechanics do I need to repair them?",
        "What is the volume of 10 litres of petrol?",
        "If my car travels 50 kms North on a road and then 50 kms South on the same road, how much distance has my car travelled?",
        "A humming bird and an eagle have a competition, who will win?",
        "IIIT-Delhi and IIT-Delhi have a competition, who will win?",
    ]
    options = [
        (["Disagree", "Agree"]),
        (["0 times", "1-2 times", "10+ times"]),
        (["Agree", "Disagree"]),
        (["Agree", "Disagree"]),
        (["10", "11", "12", "13"]),
        (["54", "63", "25", "61"]),
        (["Agree", "Disagree"]),
        (["Never", "1-10 Times", "10+ Times"]),
        (["Agree", "Disagree"]),
        (["Agree", "Disagree"]),
        (["Agree", "Disagree"]),
        (["42", "13", "7", "6"]),
        (["444", "36", "10", "2"]),
        (["84", "4", "10", "0"]),
        (["14", "100", "2000", "14000"]),
        (["28", "2", "2000", "200"]),
        (["500", "0", "5", "50"]),
        (["20 years", "48 years", "188 years", "88 years"]),
        (["6 years", "60 years", "600 years", "6000 years"]),
        (
            [
                "1 rupee = 1 dollar",
                "10000 rupee = 1 dollar",
                "1 rupee = 10000 dollar",
                "80 rupee = 1 dollar",
            ]
        ),
        (["Pakistan", "USA", "Canada", "London"]),
        (["Agree", "Disagree"]),
        (["Agree", "Disagree"]),
        (["Agree", "Disagree"]),
        (["Agree", "Disagree"]),
        (["True", "False", "Can’t say"]),
        (["True", "False", "Can’t say"]),
        (["2 hours", "24 hours", "244 hours", "2000 hours"]),
        (["100%", "10%", "40%", "33%"]),
        (
            [
                "Alps to the Pacific Ocean",
                "Himalayas to the Indian Ocean",
                "Rockies to the the Antarctic Ocean",
                "Andes to the Atlantic Ocean",
            ]
        ),
        (["1", "4", "10", "100"]),
        (["1 L", "10 L", "10 kg", "10 m"]),
        (["50 kms", "100 kms", "150 kms", "200 kms"]),
        (
            [
                "Frog or Tadpole",
                "Hummingbird or Eagle",
                "Mango tree or Banyan tree",
                "IIIT-Delhi or IIT-Delhi",
            ]
        ),
        (
            [
                "BITS-Pilani or BITS Goa",
                "IIIT-Delhi or IIT-Delhi",
                "Stanford or MIT",
                "IIIT-Delhi or IIT-Delhi",
            ]
        ),
    ]

    check = forms.ChoiceField(
        choices=[],
        widget=forms.RadioSelect,
        label="",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        label, options = random.choice(list(zip(self.questions, self.options)))
        self.fields["check"].label = label
        self.fields["check"].choices = [(i, i) for i in options]


class GazeModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    gaze_x = models.TextField(blank=True, null=False)
    gaze_y = models.TextField(blank=True, null=False)


class GazeForm(forms.ModelForm):
    class Meta:
        model = GazeModel
        fields = ["user", "video", "gaze_x", "gaze_y"]
        widgets = {
            "user": forms.HiddenInput(),
            "video": forms.HiddenInput(),
            "gaze_x": forms.HiddenInput(attrs={"id": "gaze_input_x"}),
            "gaze_y": forms.HiddenInput(attrs={"id": "gaze_input_y"}),
        }


@login_required
def video_view(request, video_id, gaze):
    video = Video.objects.get(id=video_id)
    src, length = video.src, video.length
    timer = random.randint(MIN_TIMER, length)

    if request.method == "POST":
        form = GazeForm(request.POST)
        if form.is_valid():
            form.save()
            user_stage = UserStage.objects.get(user=request.user)
            user_stage.update()
            return redirect("/experience")

    else:
        attn_form, gaze_form = AttentionCheckField(), GazeForm(
            initial={"user": request.user.id, "video": video.id}
        )
        return render(
            request,
            "form/video.html",
            {
                "src": src,
                "timer": timer,
                "time_limit": TIME_LIMIT,
                "attn_form": attn_form,
                "gaze_form": gaze_form,
                "gaze": gaze,
            },
        )
