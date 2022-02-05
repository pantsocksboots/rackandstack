from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Cohort(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)

    def __str__(self):
        return f"{self.name}"


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)

    def __str__(self):
        return f"{self.name}"


class Source(models.Model):
    name = models.CharField(max_length=30, unique=True, null=False)

    def __str__(self):
        return f"{self.name}"


class Student(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    cohort = models.ForeignKey(
        Cohort, null=True, blank=True, on_delete=models.DO_NOTHING
    )
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.DO_NOTHING)
    candidate_number = models.CharField(
        max_length=10, null=False, unique=True
    )  # ex. "CN110" or "CN012" or DoDID number
    source = models.ForeignKey(
        Source, null=True, blank=True, on_delete=models.DO_NOTHING
    )

    class Status(models.TextChoices):
        ACTIVE = "act", "Active"
        DOR = "dor", "DOR"
        MEDDROP = "med", "Medical Drop"
        PERFDROP = "perf", "Performance Drop"

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE, null=False
    )
    status_comment = models.CharField(max_length=240, null=True, blank=True, default="")
    image = models.ImageField(
        upload_to="images/", default="default_pic.png", null=False, blank=False
    )

    def __str__(self):
        return f"{self.user_id.last_name}, {self.user_id.first_name}"

    def name(self):
        return f"{self.user_id.last_name}, {self.user_id.first_name}"

    def username(self):
        return f"{self.user_id.username}"
