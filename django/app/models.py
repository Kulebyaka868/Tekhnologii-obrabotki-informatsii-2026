"""
Definition of models.
"""

from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserProfile(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.FileField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name='Номер телефона')
    address = models.TextField(null=True, blank=True, verbose_name='Адрес доставки')

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'

class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    url = models.SlugField(max_length=255, blank=True)
        
class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.FloatField()
    remain = models.IntegerField()
    description = models.TextField(null=True, blank=True)

class Image(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    path = models.FileField()

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('ready', 'Готов'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменён')
    ]
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

class OrderProduct(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    count = models.IntegerField()
    price = models.FloatField()
    
class Review(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    grade = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

class News(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    short_info = models.TextField()
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class NewsComments(models.Model):
    id = models.BigAutoField(primary_key=True)
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Комментарий от на статью {self.news.title}'

class NewsImages(models.Model):
    id = models.BigAutoField(primary_key=True)
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    path = models.FileField()

    def __str__(self):
        return f'Картинка для новости {self.news.title}'

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_username', 'created_at', 'status']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username']
    list_editable = ['status']

    def get_username(self, obj):
        return format_html('<a href="{}">{}</a>',
            reverse('admin:auth_user_change', args=[obj.user.id]),
            obj.user.username)
    get_username.short_description = 'Пользователь'
    get_username.admin_order_field = 'user__username'

class UserAdmin(BaseUserAdmin):
    def get_phone(self, obj):
        profile = UserProfile.objects.filter(user=obj).first()
        return profile.phone if profile else '-'
    get_phone.short_description = 'Телефон'

    def get_address(self, obj):
        profile = UserProfile.objects.filter(user=obj).first()
        return profile.address if profile else '-'
    get_address.short_description = 'Адрес'

    list_display = BaseUserAdmin.list_display + ('get_phone', 'get_address')

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # Только для существующих пользователей
            profile = UserProfile.objects.filter(user=obj).first()
            if not profile:
                profile = UserProfile.objects.create(user=obj)
                
            fieldsets = list(fieldsets)
            fieldsets.append(
                ('Дополнительная информация', {
                    'fields': ('user_phone', 'user_address'),
                })
            )
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:  # Только для существующих пользователей
            return readonly_fields + ('user_phone', 'user_address')
        return readonly_fields

    def user_phone(self, obj):
        profile = UserProfile.objects.filter(user=obj).first()
        return profile.phone if profile else '-'
    user_phone.short_description = 'Телефон'

    def user_address(self, obj):
        profile = UserProfile.objects.filter(user=obj).first()
        return profile.address if profile else '-'
    user_address.short_description = 'Адрес'

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'phone', 'address']
    search_fields = ['user__username', 'phone', 'address']
    list_filter = ['user']

    def get_username(self, obj):
        return format_html('<a href="{}">{}</a>',
            reverse('admin:auth_user_change', args=[obj.user.id]),
            obj.user.username)
    get_username.short_description = 'Пользователь'
    get_username.admin_order_field = 'user__username'

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_username', 'product', 'grade', 'get_short_text']
    list_filter = ['grade', 'product']
    search_fields = ['user__username', 'text', 'product__name']

    def get_username(self, obj):
        return format_html('<a href="{}">{}</a>',
            reverse('admin:auth_user_change', args=[obj.user.id]),
            obj.user.username)
    get_username.short_description = 'Пользователь'
    get_username.admin_order_field = 'user__username'

    def get_short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    get_short_text.short_description = 'Текст отзыва'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Image)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(News)
admin.site.register(NewsComments)
admin.site.register(NewsImages)