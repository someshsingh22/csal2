import random

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserStage(models.Model):
    """
    UserStage model to keep track of the stage of the user
    Sets Last Updated to the time of creation of the object for the first time
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stage = models.IntegerField(default=0)
    last_updated = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.stage}"

    def update(self):
        self.stage += 1
        self.last_updated = timezone.now()
        self.save()


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Video(models.Model):
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    src = models.CharField(max_length=100)
    length = models.IntegerField()
    desc = models.CharField(max_length=600)

    def __str__(self):
        return self.name


class VideoScene(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    url = models.CharField(max_length=100)

    def __str__(self):
        return self.url


class Experience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    videos = models.ManyToManyField(Video)
    gaze = models.IntegerField(default=0)
    brands_seen_options = models.ManyToManyField(Brand, related_name="brands_seen")
    prod_used_options = models.ManyToManyField(Brand, related_name="prod_used")
    brand_recog = models.ManyToManyField(Brand, related_name="brand_recog_options")
    scene_seen = models.ManyToManyField(VideoScene, related_name="scene_seen_options")

    def __str__(self):
        return f"{self.user.username} - {self.videos.all()}"
