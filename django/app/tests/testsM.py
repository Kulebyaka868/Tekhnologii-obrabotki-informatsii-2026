from django.test import TestCase
from app.models import UserProfile, Category, Product, Image, Order, OrderProduct, Review, News, NewsComments, NewsImages
from django.contrib.auth.models import User
from datetime import datetime

class UserProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='testuser', password='12345')
        UserProfile.objects.create(user=user, avatar='test_avatar.jpg')

    def test_user_profile_user_field(self):
        profile = UserProfile.objects.get(id=1)
        self.assertEqual(profile.user.username, 'testuser')

    def test_user_profile_avatar_field(self):
        profile = UserProfile.objects.get(id=1)
        self.assertEqual(profile.avatar, 'test_avatar.jpg')

class CategoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Category.objects.create(name='Test Category', url='test-category')

    def test_category_name_field(self):
        category = Category.objects.get(id=1)
        self.assertEqual(category.name, 'Test Category')

    def test_category_url_field(self):
        category = Category.objects.get(id=1)
        self.assertEqual(category.url, 'test-category')

class ProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Test Category', url='test-category')
        Product.objects.create(category=category, name='Test Product', price=10.99, remain=100, description='Test Description')

    def test_product_name_field(self):
        product = Product.objects.get(id=1)
        self.assertEqual(product.name, 'Test Product')

    def test_product_price_field(self):
        product = Product.objects.get(id=1)
        self.assertEqual(product.price, 10.99)

class ImageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Test Category', url='test-category')
        product = Product.objects.create(category=category, name='Test Product', price=10.99, remain=100, description='Test Description')
        Image.objects.create(product=product, path='test_image.jpg')

    def test_image_product_field(self):
        image = Image.objects.get(id=1)
        self.assertEqual(image.product.name, 'Test Product')

    def test_image_path_field(self):
        image = Image.objects.get(id=1)
        self.assertEqual(image.path, 'test_image.jpg')

class OrderModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='testuser', password='12345')
        Order.objects.create(user=user)

    def test_order_user_field(self):
        order = Order.objects.get(id=1)
        self.assertEqual(order.user.username, 'testuser')

    def test_order_created_at_field(self):
        order = Order.objects.get(id=1)
        self.assertIsInstance(order.created_at, datetime)

class OrderProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Test Category', url='test-category')
        product = Product.objects.create(category=category, name='Test Product', price=10.99, remain=100, description='Test Description')
        user = User.objects.create_user(username='testuser', password='12345')
        order = Order.objects.create(user=user)
        OrderProduct.objects.create(product=product, order=order, count=1, price=10.99)

    def test_order_product_product_field(self):
        order_product = OrderProduct.objects.get(id=1)
        self.assertEqual(order_product.product.name, 'Test Product')

    def test_order_product_order_field(self):
        order_product = OrderProduct.objects.get(id=1)
        self.assertEqual(order_product.order.user.username, 'testuser')

class ReviewModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Test Category', url='test-category')
        product = Product.objects.create(category=category, name='Test Product', price=10.99, remain=100, description='Test Description')
        user = User.objects.create_user(username='testuser', password='12345')
        Review.objects.create(product=product, user=user, text='Test review', grade=5)

    def test_review_product_field(self):
        review = Review.objects.get(id=1)
        self.assertEqual(review.product.name, 'Test Product')

    def test_review_user_field(self):
        review = Review.objects.get(id=1)
        self.assertEqual(review.user.username, 'testuser')

class NewsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='testuser', password='12345')
        News.objects.create(user=user, title='Test News', short_info='Test short info', text='Test text')

    def test_news_title_field(self):
        news = News.objects.get(id=1)
        self.assertEqual(news.title, 'Test News')

    def test_news_user_field(self):
        news = News.objects.get(id=1)
        self.assertEqual(news.user.username, 'testuser')
        
class NewsCommentsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='testuser', password='12345')
        news = News.objects.create(user=user, title='Test News', short_info='Test short info', text='Test text')
        NewsComments.objects.create(news=news, user=user, comment='Test comment')

    def test_news_comments_news_field(self):
        news_comment = NewsComments.objects.get(id=1)
        self.assertEqual(news_comment.news.title, 'Test News')

    def test_news_comments_user_field(self):
        news_comment = NewsComments.objects.get(id=1)
        self.assertEqual(news_comment.user.username, 'testuser')

class NewsImagesModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='testuser', password='12345')
        news = News.objects.create(user=user, title='Test News', short_info='Test short info', text='Test text')
        NewsImages.objects.create(news=news, path='test_image.jpg')

    def test_news_images_news_field(self):
        news_image = NewsImages.objects.get(id=1)
        self.assertEqual(news_image.news.title, 'Test News')

    def test_news_images_path_field(self):
        news_image = NewsImages.objects.get(id=1)
        self.assertEqual(news_image.path, 'test_image.jpg')
