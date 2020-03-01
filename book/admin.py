
from django.contrib import admin

# Register your models here.
from .models import Book, Category, Seller, Buyer, Type, ResumoMensal
# Register your models here.
admin.site.register(Book)
admin.site.register(ResumoMensal)
admin.site.register(Category)
admin.site.register(Seller)
admin.site.register(Buyer)
admin.site.register(Type)
