# Standard library imports.

# Related third party imports.
from django.urls import path
from tom_alerts.views import BrokerQueryListView

# Local application/library specific imports.
from . import views

# TODO: Add app_name and update paths and URL lookups.
# TODO: Make unified path formats.

urlpatterns = [path("targets/<int:pk>/delete/", views.GOATSTargetDeleteView.as_view(),
                    name="target-delete"),
               path("alerts/query/<int:pk>/update-name", views.update_brokerquery_name,
                    name="update-brokerquery-name"),
               path("observations/<int:pk>/delete-data-products/", views.DeleteObservationDataProductsView.
                    as_view(), name="delete-observation-data-products"),
               path("observations/<int:pk>/", views.GOATSObservationRecordDetailView.as_view(),
                    name="observation-detail"),
               path("dataproducts/data/<int:pk>/delete/", views.GOATSDataProductDelieteView.as_view(),
                    name="delete-dataproduct"),
               path("observations/<int:pk>/delete/", views.ObservationRecordDeleteView.as_view(),
                    name="delete"),
               path("brokers/list/", BrokerQueryListView.as_view(), name="list"),
               path("receive_query/", views.receive_query, name="receive_query"),
               path("users/<int:pk>/generate_token/", views.UserGenerateTokenView.as_view(),
                    name="user-generate-token"),
               path("users/<int:pk>/goa_login/", views.GOALoginView.as_view(), name="user-goa-login"),
               path("goa_query/<int:pk>/", views.GOAQueryFormView.as_view(), name="goa_query"),
               path("api/ongoing-tasks/", views.ongoing_tasks, name="ongoing_tasks"),
               path("recent-downloads/", views.recent_downloads, name="recent_downloads"),]
