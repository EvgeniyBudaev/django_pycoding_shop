from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()  # это говорит что мы хотим использовать того юзера, который указан у нас в settings


# 1 Category - категория
# 2 Product - продукт
# 3 CartProduct - карточка продукта
# 4 Cart - корзина
# 5 Order - заказ
# 6 Customer - покупатель
# 7 Specification - характеристики продукта


class Category(models.Model):
  name = models.CharField(max_length=255,
                          verbose_name='Имя категории')  # verbose_name - это чтобы в админке колонка таблицы так называлась
  slug = models.SlugField(
    unique=True)  # конечный endpoint, к примеру /categories/notebooks/, т.е. notebooks это наш slug

  def __str__(self):  # для того, чтобы категории представить в нашей админке
    return self.name


class Product(models.Model):
  class Meta:
    abstract = True

  category = models.ForeignKey(Category, verbose_name='Категория',
                               on_delete=models.CASCADE)  # CASCADE - говорит, что надо удалить все связи с этим объектом
  title = models.CharField(max_length=255, verbose_name='Наименование')
  slug = models.SlugField(unique=True)
  image = models.ImageField(verbose_name='Изображение')
  description = models.TextField(verbose_name='Описание', null=True)  # null=True - поле может быть пустым
  price = models.DecimalField(max_digits=9, decimal_places=2,
                              verbose_name='Цена')  # decimal_places - количество цифр после запятой

  def __str__(self):
    return self.title


class Notebook(Product):
  diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
  display_type = models.CharField(max_length=255, verbose_name='Тип дисплея')
  processor_freq = models.CharField(max_length=255, verbose_name='Частота процессора')
  ram = models.CharField(max_length=255, verbose_name='Оперативная память')
  video = models.CharField(max_length=255, verbose_name='Видеокарта')
  time_without_charge = models.CharField(max_length=255, verbose_name='Время работы аккумулятора')

  def __str__(self):
    return f'{self.category.name} : {self.title}'


class Smartphone(Product):
  diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
  display_type = models.CharField(max_length=255, verbose_name='Тип дисплея')
  resolution = models.CharField(max_length=255, verbose_name='Разрешение экрана')
  accum_volume = models.CharField(max_length=255, verbose_name='Объем батареи')
  ram = models.CharField(max_length=255, verbose_name='Оперативная память')
  sd = models.BooleanField(default=True)  # поддержка sd карт
  sd_volume_max = models.CharField(max_length=255, verbose_name='Максимальный объем встраиваемой памяти')
  main_cam_mp = models.CharField(max_length=255, verbose_name='Главная камера')
  frontal_cam_mp = models.CharField(max_length=255, verbose_name='Фронтальная камера')

  def __str__(self):
    return f'{self.category.name} : {self.title}'


class CartProduct(models.Model):
  user = models.ForeignKey('Customer', verbose_name='Покупатель',
                           on_delete=models.CASCADE)  # 'Customer' в строке т.к. модель Customer не объявлена ранее
  cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE,
                           related_name='related_products')  # Мы хотим узнать к какой корзине cartproduct относиться.  cartproduct.related_cart.метод()
  # ContentType видит все модели, которые есть в проекте
  # object_id - идентификатор инстанса этой модели
  # content_type: p = NotebookProduct.objects.get(pk=1) и далее cp = CartProduct.objects.create(content_object=p)
  content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
  object_id = models.PositiveIntegerField()
  content_object = GenericForeignKey('content_type', 'object_id')
  qty = models.PositiveIntegerField(default=1)  # PositiveIntegerField - models.PositiveIntegerField
  final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

  def __str__(self):
    return f'Продукт {self.product.title} (для корзины)'


class Cart(models.Model):
  owner = models.ForeignKey('Customer', verbose_name='Владелец', on_delete=models.CASCADE)  # owner - владелец
  products = models.ManyToManyField(CartProduct, blank=True,
                                    related_name='related_cart')  # blank=True - данное поле не обязательно к заполнению. cart.related_products.all() получаем querySet со всеми продуктами, которые в данный момент находятся в данной корзине
  total_products = models.PositiveIntegerField(default=0)
  final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

  def __str__(self):
    return str(self.id)


class Customer(models.Model):
  user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
  phone = models.CharField(max_length=20, verbose_name='Номер телефона')
  address = models.CharField(max_length=20, verbose_name='Адрес')

  def __str__(self):
    return f'Покупатель {self.user.first_name} {self.user.last_name}'
