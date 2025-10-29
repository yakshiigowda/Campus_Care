from django.db import models

class Student(models.Model):
    usn = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50)
    branch = models.CharField(max_length=50)
    year = models.IntegerField()

    def __str__(self):
        return self.name


class Teacher(models.Model):
    isn = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50)
    dept = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class HealthRecord(models.Model):
    record_id = models.AutoField(primary_key=True)
    condition_details = models.TextField()
    date_recorded = models.DateField(auto_now_add=True)
    patient_type = models.CharField(max_length=10, choices=[('Student', 'Student'), ('Teacher', 'Teacher')])
    usn = models.ForeignKey(Student, null=True, blank=True, on_delete=models.CASCADE)
    isn = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Record {self.record_id}"


class DoctorNote(models.Model):
    note_id = models.AutoField(primary_key=True)
    record = models.ForeignKey(HealthRecord, on_delete=models.CASCADE)
    note_text = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note {self.note_id}"