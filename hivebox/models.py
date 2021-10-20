from django.db import models

class Samples(models.Model):
    hive = models.IntegerField(blank=False, null=False)
    sample_time = models.DateTimeField(blank=False, null=False)
    temp_low = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    temp_high = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    temp_hot = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    temp_out = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
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
        managed = True
    

class SamplesH(models.Model):
    hive = models.IntegerField(blank=False, null=False)
    sample_time = models.DateTimeField(blank=False, null=False)
    temp_low = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    temp_high = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    temp_hot = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    temp_out = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
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
        managed = True

    def __str__(self):
        return f'Sample hive:{self.hive}, sample_time:{self.sample_time}'

class SamplesRange(models.Model):
    hive = models.IntegerField(blank=False, null=False)
    sample_time = models.CharField(max_length=44, blank=False, null=False)
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
        managed = False