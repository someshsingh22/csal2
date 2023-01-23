from django.contrib import admin

from .intro import UserStage


class UserStageAdmin(admin.ModelAdmin):
    pass


admin.site.register(UserStage, UserStageAdmin)
