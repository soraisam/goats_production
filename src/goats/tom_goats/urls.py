
from django.urls import path
from tom_alerts.views import BrokerQueryListView
from . import views

# from tom_common.api_router import SharedAPIRootRouter
# router = SharedAPIRootRouter()
# router.register("tom_goats", YourAppModelViewSet)
# app_name = "brokers"

urlpatterns = [
    path("brokers/list/", BrokerQueryListView.as_view(), name="list"),
    path('receive_query/', views.receive_query, name='receive_query'),
]
