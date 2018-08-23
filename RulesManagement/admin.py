from django.contrib import admin

# Register your models here.
from RulesManagement.models import FieldReference, FieldReferenceAdmin

admin.site.register(FieldReference, FieldReferenceAdmin)
