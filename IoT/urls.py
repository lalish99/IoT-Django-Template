from rest_framework.routers import DefaultRouter
from django.urls import include, path
from IoT import views
from IoT.api import views as api_views

router = DefaultRouter()
router.register(r'g',api_views.IoTProjectsViewSet,basename='iot_general_api')

urlpatterns = [
    path('api/',include((router.urls,'iot_api'))),
    path('<int:project_id>/<int:sensor_id>/plot/', views.sensor_graph, name="sensor_graph"),
    path('<int:project_id>/<int:sensor_id>/plot/<slug:measurement_type>/', views.graph, name="sensor_specific_graph"),
    path('<int:project_id>/<int:zone_id>/plot_zone/<slug:measurement_type>/', views.graph_mixed, name="sensor_mixed_graph"),
]