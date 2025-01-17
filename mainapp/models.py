from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.utils import timezone

User = get_user_model()  # это говорит что мы хотим использовать того юзера, который указан у нас в settings


def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]


def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


class CategoryManager(models.Manager):
    CATEGORY_NAME_COUNT_NAME = {
        'Ноутбуки': 'notebook__count',
        'Смартфоны': 'smartphone__count'
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_left_sidebar(self):
        models = get_models_for_count('notebook', 'smartphone')
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name]))
            for c in qs
        ]
        return data


class LatestProductsManager:
    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by(
                '-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(
                        products,
                        key=lambda x: x.__class__._meta.model_name.startswith(
                            with_respect_to), reverse=True
                    )
        return products


class LatestProducts:
    objects = LatestProductsManager()


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
    objects = CategoryManager()

    def __str__(self):  # для того, чтобы категории представить в нашей админке
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Категория',
                                 on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Наименование')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField(verbose_name='Описание', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2,
                                verbose_name='Цена')

    def __str__(self):
        return self.title

    def get_model_name(self):
        return self.__class__.__name__.lower()


# class Product(models.Model):
#   MIN_RESOLUTION = (400, 400)
#   MAX_RESOLUTION = (800, 800)
#   MAX_IMAGE_SIZE = 3145728
#
#   class Meta:
#     abstract = True
#
#   category = models.ForeignKey(Category, verbose_name='Категория',
#                                on_delete=models.CASCADE)  # CASCADE - говорит, что надо удалить все связи с этим объектом
#   title = models.CharField(max_length=255, verbose_name='Наименование')
#   slug = models.SlugField(unique=True)
#   image = models.ImageField(verbose_name='Изображение')
#   description = models.TextField(verbose_name='Описание', null=True)  # null=True - поле может быть пустым
#   price = models.DecimalField(max_digits=9, decimal_places=2,
#                               verbose_name='Цена')  # decimal_places - количество цифр после запятой
#
#   def __str__(self):
#     return self.title
#
#   def save(self, *args, **kwargs):
#     # image = self.image
#     # img = Image.open(image)
#     # min_height, min_width = self.MIN_RESOLUTION
#     # max_height, max_width = self.MAX_RESOLUTION
#     # if img.height < min_height or img.width < min_width:
#     #   raise MinResolutionErrorException('Разрешение изображения меньше минимального!')
#     # if img.height > max_height or img.width > max_width:
#     #   raise MaxResolutionErrorException('Разрешение изображения больше максимального!')
#     image = self.image
#     img = Image.open(image)
#     new_img = img.convert('RGB')
#     resized_new_image = new_img.resize((200, 200), Image.ANTIALIAS)
#     filestream = BytesIO()
#     resized_new_image.save(filestream, 'JPEG', quality=90)
#     filestream.seek(0)  # возвращаем каретку в начало
#     name = '{}.{}'.format(*self.image.name.split('.'))
#     self.image = InMemoryUploadedFile(filestream, 'ImageField', name, 'jpeg/image', sys.getsizeof(filestream), None)
#     super().save(*args, **kwargs)
#
#     def get_model_name(self):
#         return self.__class__.__name__.lower()


class Notebook(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
    display_type = models.CharField(max_length=255, verbose_name='Тип дисплея')
    processor_freq = models.CharField(max_length=255,
                                      verbose_name='Частота процессора')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    video = models.CharField(max_length=255, verbose_name='Видеокарта')
    time_without_charge = models.CharField(max_length=255,
                                           verbose_name='Время работы аккумулятора')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class Smartphone(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
    display_type = models.CharField(max_length=255, verbose_name='Тип дисплея')
    resolution = models.CharField(max_length=255,
                                  verbose_name='Разрешение экрана')
    accum_volume = models.CharField(max_length=255,
                                    verbose_name='Объем батареи')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    sd = models.BooleanField(default=True, verbose_name='Наличие SD карты')
    sd_volume_max = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name='Максимальный объем встраиваемой памяти'
    )
    main_cam_mp = models.CharField(max_length=255,
                                   verbose_name='Главная камера')
    frontal_cam_mp = models.CharField(max_length=255,
                                      verbose_name='Фронтальная камера')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')

    # @property
    # def sd(self):
    #     if self.sd:
    #         return 'Да'
    #     return 'Нет'


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Покупатель',
                             on_delete=models.CASCADE)  # 'Customer' в строке т.к. модель Customer не объявлена ранее
    cart = models.ForeignKey('Cart', verbose_name='Корзина',
                             on_delete=models.CASCADE,
                             related_name='related_products')  # Мы хотим узнать к какой корзине cartproduct относиться.  cartproduct.related_cart.метод()
    # ContentType видит все модели, которые есть в проекте
    # object_id - идентификатор инстанса этой модели
    # content_type: p = NotebookProduct.objects.get(pk=1) и далее cp = CartProduct.objects.create(content_object=p)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(
        default=1)  # PositiveIntegerField - models.PositiveIntegerField
    final_price = models.DecimalField(max_digits=9, decimal_places=2,
                                      verbose_name='Общая цена')

    def __str__(self):
        return f'Продукт {self.content_object.title} (для корзины)'


class Cart(models.Model):
    owner = models.ForeignKey('Customer', verbose_name='Владелец',
                              on_delete=models.CASCADE)  # owner - владелец
    products = models.ManyToManyField(CartProduct, blank=True,
                                      related_name='related_cart')  # blank=True - данное поле не обязательно к заполнению. cart.related_products.all() получаем querySet со всеми продуктами, которые в данный момент находятся в данной корзине
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2,
                                      verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь',
                             on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.CharField(max_length=20, verbose_name='Адрес')
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя',
                                    related_name='related_customer')

    def __str__(self):
        return f'Покупатель {self.user.first_name} {self.user.last_name}'


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен'),
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупатель',
                                 related_name='related_orders',
                                 on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.CharField(max_length=1024, verbose_name='Адрес', null=True,
                               blank=True)
    status = models.CharField(max_length=100, verbose_name='Статус заказа',
                              choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=100, verbose_name='Тип заказа',
                                   choices=BUYING_TYPE_CHOICES,
                                   default=BUYING_TYPE_SELF)
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True,
                               blank=True)
    created_at = models.DateTimeField(auto_now=True,
                                      verbose_name='Дата создания заказа')
    order_date = models.DateTimeField(verbose_name='Дата получения заказа',
                                      default=timezone.now)

    def __str__(self):
        return str(self.id)
