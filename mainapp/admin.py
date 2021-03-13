from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, ModelForm
from PIL import Image
from django import forms

from .models import *


class NotebookADminForm(ModelForm):
  MIN_RESOLUTION = (400, 400)

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['image'].help_text = f'Загружайте изображения с минимальным разрешением {self.MIN_RESOLUTION}'

  def clean_image(self):
    image = self.cleaned_data['image']
    img = Image.open(image)
    min_height, min_width = self.MIN_RESOLUTION
    if img.height < min_height or img.width < min_width:
      raise ValidationError('Разрешение изображения меньше минимального!')
    return image


class NotebookAdmin(admin.ModelAdmin):
  form = NotebookADminForm

  def formfield_for_foreignkey(self, db_field, request, **kwargs):
    if db_field.name == 'category':
      return ModelChoiceField(Category.objects.filter(slug='notebooks'))
    return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SmartphoneAdmin(admin.ModelAdmin):
  def formfield_for_foreignkey(self, db_field, request, **kwargs):
    if db_field.name == 'category':
      return ModelChoiceField(Category.objects.filter(slug='smartphones'))
    return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Notebook, NotebookAdmin)
admin.site.register(Smartphone, SmartphoneAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
