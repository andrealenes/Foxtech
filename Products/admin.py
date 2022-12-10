from django.contrib import admin
from .models import Product
from .models import Category
from .models import UnitOfMeasure

@admin.register(Product) 
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id_product", "name", "unit_price", "final_price", "reference", "inputs", "outputs", "stock", "discount", "modified", "state"]
    list_display_links = ["name"] 
    list_editable = ["unit_price","inputs", "outputs", "discount"] 
    search_fields = ["name", "reference"] 
    list_per_page = 15

    fieldsets = (
        ("Informacion del producto", {
            'fields': ('name', 'description', 'image', 'unit_price', 'stock', 'discount', 'unit_of_measure', 'state', )
        }),
    )

@admin.register(Category) 
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "modified", "state"]
    list_display_links = ["name"] 
    search_fields = ["name"] 
    list_per_page = 12

    fieldsets = (
        ("Informacion de la categoria", {
            'fields': ('name', 'description', 'products', 'state', )
        }),
    )

@admin.register(UnitOfMeasure) 
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ["name", "modified", "state"]
    list_display_links = ["name"] 
    search_fields = ["name"] 
    list_per_page = 12

    fieldsets = (
        ("Descripcion",{
            'fields': ('name', 'state', )
        }),
    )