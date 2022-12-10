from django.contrib import admin
from .models import City
from .models import TypeOfDocument
from .models import UserModel

@admin.register(City) 
class CityAdmin(admin.ModelAdmin):
    list_display = ["description", "zip_code", "modified", "state"]
    list_display_links = ["description"] 
    search_fields = ["description", "zip_code"] 
    list_per_page = 10

@admin.register(TypeOfDocument) 
class TypeOfDocumentAdmin(admin.ModelAdmin):
    list_display = ["description", "modified", "state"]
    list_display_links = ["description"] 

@admin.register(UserModel) 
class UserModelAdmin(admin.ModelAdmin):
    list_display = ["id_user", "first_name", "last_name", "email", "phone_number", "is_staff", "is_active", "create", "modified"]
    list_display_links = ["id_user"] 