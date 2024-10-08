from django.urls import path
from .views import *

urlpatterns = [
    path('', InvestmentAnalysisView.as_view(), name='policy_analysis'),
]
