from django.db import models

class Products(models.Model):
    ProductID = models.IntegerField(null=True, blank=True)
    Manufacturer = models.CharField(max_length=200, null=True, blank=True)
    Name = models.CharField(max_length=200, null=True, blank=True)
    Price = models.CharField(max_length=200, null=True, blank=True)
    Car_type = models.CharField(max_length=200, null=True, blank=True)
    season = models.CharField(max_length=200, null=True, blank=True)
    tire_width = models.CharField(max_length=200, null=True, blank=True)
    size = models.CharField(max_length=200, null=True, blank=True)
    approval = models.CharField(max_length=200, null=True, blank=True)
    speed_index = models.CharField(max_length=200, null=True, blank=True)
    weight_index = models.CharField(max_length=200, null=True, blank=True)
    sound_index = models.CharField(max_length=200, null=True, blank=True)
    production_year = models.CharField(max_length=200, null=True, blank=True)
    country_of_origin = models.CharField(max_length=200, null=True, blank=True)
    guaranty = models.CharField(max_length=200, null=True, blank=True)
    other_info = models.TextField(null=True, blank=True)
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return (self.Manufacturer + " " + self.Name)
