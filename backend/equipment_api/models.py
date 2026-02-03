from django.db import models

class Equipment(models.Model):
    name = models.CharField(max_length=100)
    equipment_type = models.CharField(max_length=50)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()

class DatasetHistory(models.Model):
    file_name = models.CharField(max_length=255)
    total_count = models.IntegerField()
    avg_pressure = models.FloatField()
    uploaded_at = models.DateTimeField(auto_now_add=True) 