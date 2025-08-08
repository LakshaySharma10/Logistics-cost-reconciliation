from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import api_view
from rest_framework import status

from django.http import HttpResponse
from decimal import Decimal
import pandas as pd
import csv
import traceback

from .models import Truck, TransportCompany
from .utils import get_company_cost_shares

# Excel File Upload
class ExcelUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        excel_file = request.FILES.get("file")

        if not excel_file:
            return Response({"error": "No file uploaded"}, status=400)

        try:
            df = pd.read_excel(excel_file)

            for _, row in df.iterrows():
                company_name = row['company']
                truck_id = row['truck_id']
                capacity = row['capacity']
                assigned_load = row['assigned_load']

                company, _ = TransportCompany.objects.get_or_create(name=company_name)

                Truck.objects.update_or_create(
                    truck_id=truck_id,
                    defaults={
                        'capacity': capacity,
                        'assigned_load': assigned_load,
                        'company': company
                    }
                )

            return Response({"message": "Excel data uploaded successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)

# Load Optimization 
@api_view(['POST'])
def optimize_load_assignments(request):
    trucks = list(Truck.objects.select_related('company').order_by('-capacity').iterator())

    if not trucks:
        return Response({"error": "No trucks available"}, status=404)

    total_load = sum(t.assigned_load for t in trucks)
    remaining_load = total_load
    optimized_assignments = []

    greedy_phase_trucks = []
    bin_packing_trucks = []

    for truck in trucks:
        if remaining_load >= truck.capacity:
            truck.assigned_load = truck.capacity
            remaining_load -= truck.capacity
            greedy_phase_trucks.append(truck)
        else:
            bin_packing_trucks.append(truck)

    if remaining_load > 0 and bin_packing_trucks:
        bin_packing_trucks.sort(key=lambda t: t.capacity)

        for truck in bin_packing_trucks:
            if remaining_load == 0:
                truck.assigned_load = 0
            elif remaining_load >= truck.capacity:
                truck.assigned_load = truck.capacity
                remaining_load -= truck.capacity
            else:
                truck.assigned_load = remaining_load
                remaining_load = 0

    all_trucks = greedy_phase_trucks + bin_packing_trucks
    for truck in all_trucks:
        optimized_assignments.append({
            "truck_id": truck.truck_id,
            "assigned_load": truck.assigned_load,
            "capacity": truck.capacity,
            "company": truck.company.name
        })

    Truck.objects.bulk_update(all_trucks, ['assigned_load'])

    return Response({
        "message": "Fleet load optimized successfully.",
        "assignments": optimized_assignments
    }, status=status.HTTP_200_OK)


# Cost Calculation View
@api_view(['POST'])
def calculate_costs(request):
    total_cost = request.data.get('total_cost')

    if not total_cost:
        return Response({"error": "Missing 'total_cost' in request"}, status=400)

    try:
        total_cost = Decimal(total_cost)
        trucks = list(Truck.objects.select_related('company').all())
        company_costs = get_company_cost_shares(trucks, total_cost)
        return Response(company_costs)

    except Exception as e:
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)

# Export: Truck Data JSON
@api_view(['GET'])
def export_truck_data_json(request):
    total_cost = request.GET.get('total_cost')

    try:
        trucks = list(Truck.objects.select_related('company').all())

        if total_cost:
            total_cost = Decimal(total_cost)
            company_costs = get_company_cost_shares(trucks, total_cost)
        else:
            company_costs = {}

        data = {
            "trucks": [
            {
                "truck_id": truck.truck_id,
                "capacity": truck.capacity,
                "assigned_load": truck.assigned_load,
                "company": truck.company.name
            }
            for truck in trucks
            ],
            "company_costs": {
                company: info["cost_share"]
                for company, info in company_costs.items()
            }
        }
        return Response(data)

    except Exception as e:
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)

# Export: Truck Data CSV
@api_view(['GET'])
def export_truck_data_csv(request):
    total_cost_param = request.GET.get('total_cost')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="truck_data.csv"'
    writer = csv.writer(response)

    writer.writerow(['Truck ID', 'Capacity', 'Assigned Load', 'Company', 'Cost Share'])

    trucks = list(Truck.objects.select_related('company').all())

    try:
        total_cost = Decimal(total_cost_param) if total_cost_param else Decimal("0.00")
    except:
        total_cost = Decimal("0.00")

    company_costs = get_company_cost_shares(trucks, total_cost)

    cost_share_per_company = {
        company: Decimal(info["cost_share"])
        for company, info in company_costs.items()
    }

    company_loads = {
        company: info["assigned_load"]
        for company, info in company_costs.items()
    }
    for truck in trucks:
        company = truck.company.name
        load = truck.assigned_load
        company_total_load = company_loads.get(company, 0)
        if company_total_load > 0:
            truck_cost_share = (
                (Decimal(load) / Decimal(company_total_load)) * cost_share_per_company[company]
            ).quantize(Decimal("0.01"))
        else:
            truck_cost_share = Decimal("0.00")

        writer.writerow([
            truck.truck_id,
            truck.capacity,
            truck.assigned_load,
            company,
            str(truck_cost_share)
        ])

    return response


