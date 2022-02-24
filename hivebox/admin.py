from django.contrib import admin

# Register your models here.
from .models import Hives, HiveGroups

""" class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 3
 """
class HivesAdmin(admin.ModelAdmin):
    # inlines = [CarModelInline]
    list_display = ['id', 'hive_id', 'name', 'user_id', 'group_id']

# CarModelAdmin class
class HiveGroupsAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'user_id')

# Register models here
admin.site.register(Hives, HivesAdmin)
admin.site.register(HiveGroups, HiveGroupsAdmin)
