from django.db import models

class Samples(models.Model):
    hive = models.IntegerField()
    sample_time = models.DateTimeField(primary_key=True)
    temp_low = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    temp_high = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    temp_hot = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    temp_out = models.SmallIntegerField(blank=True, null=True)
    temp_target = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    humi_in = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    humi_out = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    heat_pwr = models.SmallIntegerField(blank=True, null=True)
    fan = models.IntegerField(blank=True, null=True)
    mode = models.CharField(max_length=10, blank=True, null=True)
    heater_breakers = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'samples'
        unique_together = (('hive', 'sample_time'),)
    

class SamplesH(models.Model):
    hive = models.IntegerField()
    sample_time = models.DateTimeField(primary_key=True)
    temp_low = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    temp_high = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    temp_hot = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    temp_out = models.SmallIntegerField(blank=True, null=True)
    temp_target = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    humi_in = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    humi_out = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    heat_pwr = models.SmallIntegerField(blank=True, null=True)
    fan = models.IntegerField(blank=True, null=True)
    mode = models.CharField(max_length=10, blank=True, null=True)
    heater_breakers = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'samples_h'
        unique_together = (('hive', 'sample_time'),)
