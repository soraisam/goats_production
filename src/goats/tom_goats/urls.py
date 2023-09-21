# Standard library imports.

# Related third party imports.
from django.urls import path
from tom_alerts.views import BrokerQueryListView

# Local application/library specific imports.
from . import views


urlpatterns = [
    path("brokers/list/", BrokerQueryListView.as_view(), name="list"),
    path('receive_query/', views.receive_query, name='receive_query'),
    path('users/<int:pk>/generate_token/', views.UserGenerateTokenView.as_view(), name='user-generate-token'),
]
