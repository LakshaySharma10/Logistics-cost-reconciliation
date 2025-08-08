from django.urls import path
from .views import ExcelUploadView, calculate_costs, optimize_load_assignments, export_truck_data_json, export_truck_data_csv

urlpatterns = [
    path('upload/', ExcelUploadView.as_view(), name='excel-upload'),
    path('calculate-costs/', calculate_costs, name='calculate-costs'),
    path('optimize-loads/', optimize_load_assignments, name='optimize-loads'),
    path('export/json/', export_truck_data_json, name='export-truck-data-json'),
    path('export/csv/', export_truck_data_csv, name='export-truck-data-csv'),
]
