from django.contrib import admin
from django.contrib.auth.models import User
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .model import AudioClip, Brand, Experience, UserStage, Video, VideoScene

TO_BE_REGISTERED = [
    "Brand",
    "Experience",
    "Video",
    "VideoScene",
    "UserStage",
    "User",
    "AudioClip",
]


class BrandResource(resources.ModelResource):
    class Meta:
        model = Brand


class ExperienceResource(resources.ModelResource):
    class Meta:
        model = Experience


class VideoResource(resources.ModelResource):
    class Meta:
        model = Video


class VideoSceneResource(resources.ModelResource):
    class Meta:
        model = VideoScene


class UserStageResource(resources.ModelResource):
    class Meta:
        model = UserStage


class AudioClipResource(resources.ModelResource):
    class Meta:
        model = AudioClip


class BrandAdmin(ImportExportModelAdmin):
    resource_class = BrandResource


class ExperienceAdmin(ImportExportModelAdmin):
    resource_class = ExperienceResource


class VideoAdmin(ImportExportModelAdmin):
    resource_class = VideoResource


class VideoSceneAdmin(ImportExportModelAdmin):
    resource_class = VideoSceneResource


class UserStageAdmin(ImportExportModelAdmin):
    resource_class = UserStageResource


class AudioClipAdmin(ImportExportModelAdmin):
    resource_class = AudioClipResource


admin.site.register(Brand, BrandAdmin)
admin.site.register(Experience, ExperienceAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(VideoScene, VideoSceneAdmin)
admin.site.register(UserStage, UserStageAdmin)
admin.site.register(AudioClip, AudioClipAdmin)
