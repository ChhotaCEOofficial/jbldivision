from django.db import models
from django.contrib.auth.models import User


class Train(models.Model):
    number = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    train_type = models.CharField(max_length=50)
    owning_zone = models.CharField(max_length=100)
    from_point = models.CharField(max_length=100)
    to_point = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.number} - {self.name}"


class Department(models.Model):
    name = models.CharField(max_length=100)


class DepartmentChoices(models.TextChoices):
    COA = 'COA', 'COA'
    MECH = 'MECH', 'Mechanical'
    FOIS = 'FOIS', 'FOIS'
    ELEC = 'ELEC', 'Electrical'


class CustomUser(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    role = models.CharField(max_length=50)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    name = models.CharField(max_length=255)
    department = models.CharField(max_length=50)
    last_updated = models.DateField(null=True, blank=True)
    manual = models.BooleanField(default=False)

from django.db import models

class ReportData(models.Model):
    name = models.CharField(max_length=255)
    department = models.CharField(max_length=100)
    date = models.DateField()
    data1 = models.TextField(blank=True, null=True)
    data2 = models.TextField(blank=True, null=True)
    data3 = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.department}"


class RailMadadReport(models.Model):
    ref_no = models.CharField(max_length=50)
    registration_date = models.DateField()
    closing_date = models.DateField(null=True, blank=True)
    complaint_description = models.TextField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.ref_no



class JabalpurOperation(models.Model):
    train_number = models.CharField(max_length=10)
    train_name = models.CharField(max_length=100)
    train_type = models.CharField(max_length=20)
    owning_zone = models.CharField(max_length=50)
    from_point = models.CharField(max_length=50)
    to_point = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.train_number} - {self.train_name}"


class UploadLog(models.Model):
    report_name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class DataEntry(models.Model):
    report_name = models.CharField(max_length=255)
    date = models.DateField()
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.report_name

class MeBasicEntry(models.Model):
    train_number = models.CharField(max_length=20)
    train_name = models.CharField(max_length=100)
    train_type = models.CharField(max_length=50)
    owning_zone = models.CharField(max_length=100)
    from_point = models.CharField(max_length=100)
    to_point = models.CharField(max_length=100)

    def __str__(self):
        return self.train_number

class StatsMonthlyEntry(models.Model):
    month = models.CharField(max_length=20)
    total_trains = models.IntegerField()
    late_trains = models.IntegerField()
    maintenance_done = models.IntegerField()

    def __str__(self):
        return self.month