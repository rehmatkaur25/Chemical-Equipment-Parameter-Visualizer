from django.contrib import admin
from django.urls import path
# Import your views from the equipment_api folder
from equipment_api.views import EquipmentUploadView, PDFReportView

urlpatterns = [
    path('admin/', admin.site.urls),
    # This MUST match the URL in your App.js exactly
    path('api/upload/', EquipmentUploadView.as_view(), name='upload'),
    path('api/report/', PDFReportView.as_view(), name='report'),
]