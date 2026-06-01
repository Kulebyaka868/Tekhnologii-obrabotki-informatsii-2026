from django.test import TestCase, Client
from django.urls import reverse
from app.models import Category, News, NewsComments, Product, Review, Image, UserProfile, User, Order, OrderProduct, Product
from app.forms import ReviewForm
from datetime import datetime
import json
from decimal import Decimal
from django.contrib.auth.models import User

class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='TestCategory', url='test-category')
        self.product = Product.objects.create(name='TestProduct', category=self.category, price=100, remain=10)
        self.review = Review.objects.create(product=self.product, user=self.user, grade=5)
        self.image = Image.objects.create(product=self.product, path='test-image.jpg')
        self.user_profile = UserProfile.objects.create(user=self.user, avatar='test-avatar.jpg')


    def test_home_page(self):
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('home'))
        
        self.assertEqual(response.status_code, 200)
        
        self.assertTemplateUsed(response, 'app/index.html')
        
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], 'Главная')
        self.assertIn('year', response.context)
        self.assertEqual(response.context['year'], datetime.now().year)
        self.assertIn('categories', response.context)
        self.assertGreater(len(response.context['categories']), 0)
        self.assertIn('products', response.context)
        self.assertGreater(len(response.context['products']), 0)
        self.assertIn('avatar', response.context)
        self.assertEqual(response.context['avatar'].avatar, 'test-avatar.jpg')
        
    def test_home_page_no_user(self):
        response = self.client.get(reverse('home'))
    
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/index.html')
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], 'Главная')
        self.assertIn('year', response.context)
        self.assertEqual(response.context['year'], datetime.now().year)
        self.assertIn('categories', response.context)
        self.assertGreater(len(response.context['categories']), 0)
        self.assertIn('products', response.context)
        self.assertGreater(len(response.context['products']), 0)
        self.assertIsNone(response.context.get('avatar'))

        
    def test_home_page_different_user(self):
        new_user = User.objects.create_user(username='anotheruser', password='54321')
        self.client.force_login(new_user)
    
        response = self.client.get(reverse('home'))
    
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/index.html')
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], 'Главная')
        self.assertIn('year', response.context)
        self.assertEqual(response.context['year'], datetime.now().year)
        self.assertIn('categories', response.context)
        self.assertGreater(len(response.context['categories']), 0)
        self.assertIn('products', response.context)
        self.assertGreater(len(response.context['products']), 0)
        self.assertIn('avatar', response.context)
        
    def test_home_page_empty_data(self):
        Category.objects.all().delete()
        Product.objects.all().delete()

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/index.html')
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], 'Главная')
        self.assertIn('year', response.context)
        self.assertEqual(response.context['year'], datetime.now().year)
        self.assertIn('categories', response.context)
        self.assertEqual(len(response.context['categories']), 0)
        self.assertIn('products', response.context)
        self.assertEqual(len(response.context['products']), 0)
        self.assertIsNone(response.context.get('avatar'))

class CatalogViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='TestCategory', url='test-category')
        self.product = Product.objects.create(name='TestProduct', category=self.category, price=100, remain=10)
        self.review = Review.objects.create(product=self.product, user=self.user, grade=5)
        self.image = Image.objects.create(product=self.product, path='test-image.jpg')
        self.user_profile = UserProfile.objects.create(user=self.user, avatar='test-avatar.jpg')

    def test_catalog_page_authenticated(self):
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('catalog'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/catalog.html')
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], 'Каталог')
        self.assertIn('year', response.context)
        self.assertEqual(response.context['year'], datetime.now().year)
        self.assertIn('categories', response.context)
        self.assertGreater(len(response.context['categories']), 0)
        self.assertIn('products', response.context)
        self.assertGreater(len(response.context['products']), 0)
        self.assertIn('avatar', response.context)
        self.assertEqual(response.context['avatar'].avatar, 'test-avatar.jpg')
        
    def test_catalog_page_not_authenticated(self):
        response = self.client.get(reverse('catalog'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/catalog.html')
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], 'Каталог')
        self.assertIn('year', response.context)
        self.assertEqual(response.context['year'], datetime.now().year)
        self.assertIn('categories', response.context)
        self.assertGreater(len(response.context['categories']), 0)
        self.assertIn('products', response.context)
        self.assertGreater(len(response.context['products']), 0)
        self.assertIn('avatar', response.context)

    def test_catalog_page_empty_data_authenticated(self):
        self.client.force_login(self.user)
        Category.objects.all().delete()
        Product.objects.all().delete()

        response = self.client.get(reverse('catalog'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/catalog.html')
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], 'Каталог')
        self.assertIn('year', response.context)
        self.assertEqual(response.context['year'], datetime.now().year)
        self.assertIn('categories', response.context)
        self.assertEqual(len(response.context['categories']), 0)
        self.assertIn('products', response.context)
        self.assertEqual(len(response.context['products']), 0)
        self.assertIn('avatar', response.context)
        self.assertEqual(response.context['avatar'].avatar, 'test-avatar.jpg')

    def test_catalog_page_empty_data_not_authenticated(self):
        Category.objects.all().delete()
        Product.objects.all().delete()

        response = self.client.get(reverse('catalog'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/catalog.html')
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], 'Каталог')
        self.assertIn('year', response.context)
        self.assertEqual(response.context['year'], datetime.now().year)
        self.assertIn('categories', response.context)
        self.assertEqual(len(response.context['categories']), 0)
        self.assertIn('products', response.context)
        self.assertEqual(len(response.context['products']), 0)
        self.assertIn('avatar', response.context)
        
class RegistrationViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_successful_registration(self):
        form_data = {
            'username': 'newuser',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        }
        
        response = self.client.post(reverse('registration'), data=form_data)
        
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        self.assertRedirects(response, reverse('home'))

    def test_unsuccessful_registration(self):
        form_data = {
            'username': 'newuser',
            'password1': 'complexpassword123',
            'password2': 'differentpassword123',
        }
        
        response = self.client.post(reverse('registration'), data=form_data)
        
        self.assertFalse(User.objects.filter(username='newuser').exists())
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/registration.html')
        self.assertIn('regform', response.context)
        self.assertTrue(response.context['regform'].errors)
        
class Dynamic1ViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='TestCategory', url='test-category')
        self.subcategory = Category.objects.create(name='SubCategory', url='sub-category', parent_id=self.category.id)
        self.product = Product.objects.create(name='TestProduct', category=self.subcategory, price=100, remain=10)
        self.review = Review.objects.create(product=self.product, user=self.user, grade=5)
        self.image = Image.objects.create(product=self.product, path='test-image.jpg')
        self.user_profile = UserProfile.objects.create(user=self.user, avatar='test-avatar.jpg')

    def test_dynamic1_existing_category(self):
        response = self.client.get(reverse('dynamic1', args=['test-category']))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/dynamic.html')
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], 'TestCategory')
        self.assertIn('category', response.context)
        self.assertEqual(response.context['category']['name'], 'TestCategory')
        self.assertIn('products', response.context)
        self.assertGreater(len(response.context['products']), 0)
        self.assertEqual(response.context['products'][0].name, 'TestProduct')
        self.assertIn('avatar', response.context)
        self.assertIsNone(response.context['avatar'])

    def test_dynamic1_nonexistent_category(self):
        response = self.client.get(reverse('dynamic1', args=['nonexistent-category']))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/dynamic.html')
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], 'Ошибка 404')
        self.assertIn('category', response.context)
        self.assertEqual(response.context['category']['name'], 'Страница не найдена')
        self.assertIn('products', response.context)
        self.assertIsNone(response.context['products'])
        self.assertIn('avatar', response.context)
        self.assertIsNone(response.context['avatar'])

        
class ProductsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='TestCategory', url='test-category')
        self.product = Product.objects.create(name='TestProduct', category=self.category, price=100, remain=10)
        self.review = Review.objects.create(product=self.product, user=self.user, grade=5, text="Great product!")
        self.image = Image.objects.create(product=self.product, path='test-image.jpg')
        self.user_profile = UserProfile.objects.create(user=self.user, avatar='test-avatar.jpg')

    def test_product_page_existing_product(self):
        response = self.client.get(reverse('products', args=[self.product.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/products.html')
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], self.product.name)
        self.assertIn('product', response.context)
        self.assertEqual(response.context['product'].name, self.product.name)
        self.assertIn('reviews', response.context)
        self.assertGreater(len(response.context['reviews']), 0)
        self.assertEqual(response.context['reviews'][0]['review'].text, 'Great product!')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], ReviewForm)
        self.assertIn('avatar', response.context)
        self.assertIsNone(response.context['avatar'])

    def test_product_page_nonexistent_product(self):
        response = self.client.get(reverse('products', args=[9999]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/products.html')
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], 'Страница не найдена')
        self.assertIn('product_data', response.context)
        self.assertEqual(response.context['product_data']['name'], 'Страница не найдена')
        self.assertIn('product', response.context)
        self.assertIsNone(response.context['product'])
        self.assertIn('reviews', response.context)
        self.assertEqual(len(response.context['reviews']), 0)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], ReviewForm)
        self.assertIn('avatar', response.context)
        self.assertIsNone(response.context['avatar'])

class CreateOrderViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        category = Category.objects.create(name='TestCategory')
        self.product = Product.objects.create(name='TestProduct', price=100, remain=10, category=category)

    def test_create_order_authenticated(self):
        self.client.login(username='testuser', password='12345')
        cart_items = {
            "cartItems": [
                {"id": self.product.id, "quantity": 1, "price": "100.00"}
            ]
        }
        response = self.client.post(reverse('create_order'), data=json.dumps(cart_items), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderProduct.objects.count(), 1)
        self.assertEqual(OrderProduct.objects.first().product, self.product)

    def test_create_order_not_authenticated(self):
        cart_items = {
            "cartItems": [
                {"id": self.product.id, "quantity": 1, "price": "100.00"}
            ]
        }
        response = self.client.post(reverse('create_order'), data=json.dumps(cart_items), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Order.objects.count(), 0)
        
class DeleteOrderViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.order = Order.objects.create(user=self.user)

    def test_delete_order_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('delete_order', args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)

    def test_delete_order_not_authenticated(self):
        response = self.client.post(reverse('delete_order', args=[self.order.id]))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Order.objects.count(), 1)

class DeleteCommentViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.news = News.objects.create(user=self.user, title='Test Title', short_info='short', text='text')
        self.comment = NewsComments.objects.create(user=self.user, news=self.news, comment='Test Comment')

    def test_delete_comment_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('delete_comment', args=[self.comment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(NewsComments.objects.count(), 0)

    def test_delete_comment_not_authenticated(self):
        response = self.client.post(reverse('delete_comment', args=[self.comment.id]))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(NewsComments.objects.count(), 1)
        
class DeleteReviewViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='TestCategory', url='test-category')
        self.product = Product.objects.create(name='TestProduct', price=100, remain=10, category=self.category)
        self.review = Review.objects.create(user=self.user, product=self.product, grade=5)

    def test_delete_review_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('delete_review', args=[self.review.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.count(), 0)

    def test_delete_review_not_authenticated(self):
        response = self.client.post(reverse('delete_review', args=[self.review.id]))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Review.objects.count(), 1)
