# Standard library imports.

# Related third party imports.
from django.urls import path
from tom_alerts.views import BrokerQueryListView

# Local application/library specific imports.
from . import views

# TODO: Add app_name and update paths and URL lookups.

urlpatterns = [path("observations/<int:pk>/delete-data-products/", views.DeleteObservationDataProductsView.
                    as_view(), name="delete-observation-data-products"),
               path("observations/<int:pk>/", views.GOATSObservationRecordDetailView.as_view(),
                    name="observation-detail"),
               path("dataproducts/data/<int:pk>/delete/", views.GOATSDataProductDelieteView.as_view(),
                    name="delete-dataproduct"),
               path("alerts/alert/create/", views.GOATSCreateTargetFromAlertView.as_view(),
                    name="create-target"),
               path("observations/<int:pk>/delete/", views.ObservationRecordDeleteView.as_view(),
                    name="delete"),
               path("targets/<int:pk>/", views.GOATSTargetDetailView.as_view(), name="detail"),
               path("observations/add/", views.GOATSAddExistingObservationView.as_view(),
                    name="add-existing"),
               path("brokers/list/", BrokerQueryListView.as_view(), name="list"),
               path("receive_query/", views.receive_query, name="receive_query"),
               path("users/<int:pk>/generate_token/", views.UserGenerateTokenView.as_view(),
                    name="user-generate-token"),
               path("users/<int:pk>/goa_login/", views.GOALoginView.as_view(), name="user-goa-login"),
               path("goa_query/<int:pk>/", views.GOAQueryFormView.as_view(), name="goa_query"),]
