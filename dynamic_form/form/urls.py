from django.urls import path
from django.views.generic import TemplateView

from .brand_qa import BrandDescQAView, BrandQAView
from .calibration import CalibrateView
from .intro import IntroView
from .popup import popup_slice
from .scene_qa import SceneQAView
from .survey import SurveyFormView
from .video import consistency_view, video_view
from .views import experience_view, home_view

urlpatterns = [
    path("", home_view, name="home"),
    path("intro/", IntroView, name="intro"),
    path("video/<int:video_id>/<int:gaze>", video_view, name="video"),
    path("popup/<int:start>,<int:end>", popup_slice, name="popup"),
    path("experience", experience_view, name="experience"),
    path("brand/<int:brand_id>", BrandQAView, name="brand"),
    path("scene/<int:scene_id>", SceneQAView, name="scene"),
    path("survey", SurveyFormView, name="survey"),
    path("calib", CalibrateView, name="calibration"),
    path("consistency_check", consistency_view, name="consistency_check"),
    path("desc/<int:brand_id>", BrandDescQAView, name="desc"),
]
