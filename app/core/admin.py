from django.contrib import admin

from core import models


admin.site.register(models.Ingredient)
admin.site.register(models.Recipe)
