from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from .models import Truck, TransportCompany
import io
import pandas as pd

class LogisticsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.company_a = TransportCompany.objects.create(name="Company A")
        self.company_b = TransportCompany.objects.create(name="Company B")

        self.truck1 = Truck.objects.create(truck_id="T1", capacity=1000, assigned_load=600, company=self.company_a)
        self.truck2 = Truck.objects.create(truck_id="T2", capacity=800, assigned_load=400, company=self.company_b)

    def test_excel_upload_view(self):
        df = pd.DataFrame([
            {"company": "Company A", "truck_id": "T3", "capacity": 1200, "assigned_load": 1000},
        ])
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        excel_buffer.seek(0)

        response = self.client.post("/api/upload/", {"file": excel_buffer}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Truck.objects.filter(truck_id="T3").exists())

    def test_optimize_load_assignments(self):
        response = self.client.post("/api/optimize-loads/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.truck1.refresh_from_db()
        self.truck2.refresh_from_db()
        self.assertEqual(self.truck1.assigned_load + self.truck2.assigned_load, 1000)

    def test_calculate_costs(self):
        response = self.client.post("/api/calculate-costs/", {"total_cost": "1000.00"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Company A", response.data)
        self.assertIn("Company B", response.data)

    def test_export_truck_data_json(self):
        response = self.client.get("/api/export/json/?total_cost=1000")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("trucks", response.data)
        self.assertIn("company_costs", response.data)

    def test_export_truck_data_csv(self):
        response = self.client.get("/api/export/csv/?total_cost=1000")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("attachment; filename=\"truck_data.csv\"", response["Content-Disposition"])
