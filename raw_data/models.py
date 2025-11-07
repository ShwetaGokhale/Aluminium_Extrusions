from django.db import models
from datetime import datetime

class Raw_data(models.Model):
    sensor_name = models.CharField(max_length=50, verbose_name="Sensor Name")
    datetime = models.DateTimeField(verbose_name="Date & Time")  # combined
    t_factor = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="T-Factor")
    die_number = models.CharField(max_length=50, verbose_name="Die Number")
    length = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Length (ft.in)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Record Created At")

    class Meta:
        db_table = "raw_machine_data"

    def __str__(self):
        return f"{self.sensor_name} @ {self.datetime} → {self.length} ft"

    @staticmethod
    def parse_datetime(date_str, time_str):
        """
        Convert machine date + time into Python datetime.
        Example: date_str='16/07/25', time_str='19:45:11'
        """
        return datetime.strptime(f"{date_str} {time_str}", "%y/%m/%d %H:%M:%S")


class ProductionData(models.Model):
    sensor_name = models.CharField(max_length=50, verbose_name="Sensor Name")
    datetime = models.DateTimeField(verbose_name="Date & Time")
    t_factor = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="T-Factor")
    die_name = models.CharField(max_length=100, verbose_name="Die Name")
    length = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Length (ft.in)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Record Created At")

    class Meta:
        db_table = "production_data"
        ordering = ["datetime"]

    def __str__(self):
        return f"{self.die_name} → {self.length} ft @ {self.datetime}"
