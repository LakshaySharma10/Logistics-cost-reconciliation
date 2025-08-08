from django.db import models

class TransportCompany(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Truck(models.Model):
    truck_id = models.CharField(max_length=10, unique=True)
    capacity = models.FloatField()
    assigned_load = models.FloatField()
    company = models.ForeignKey(TransportCompany, on_delete=models.CASCADE, related_name='trucks')

    def __str__(self):
        return f"{self.truck_id} ({self.company.name})"
