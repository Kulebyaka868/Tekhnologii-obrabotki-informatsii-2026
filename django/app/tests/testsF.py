from django.test import TestCase
from app.forms import UserProfileForm, AnketaForm, NewsForm, ReviewForm, NewsCommentForm

class FormsTestCase(TestCase):
    def test_user_profile_form_valid(self):
        form_data = {
            'avatar': 'valid_avatar.jpg',
        }
        form = UserProfileForm(data=form_data, files=form_data)
        self.assertFalse(form.is_valid())

    def test_user_profile_form_invalid(self):
        form_data = {'avatar': 'not_an_image.txt'}
        form = UserProfileForm(data=form_data, files=form_data)
        self.assertFalse(form.is_valid())

    def test_anketa_form_valid(self):
        form_data = {
            'name': 'John Doe',
            'city': 'New York',
            'job': 'Developer',
            'gender': '1',
            'internet': '3',
            'email': 'john@example.com',
            'notice': True,
            'message': 'Lorem ipsum dolor sit amet.'
        }
        form = AnketaForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_anketa_form_invalid(self):
        form_data = {
            'name': 'John Doe',
            'city': 'New York',
            'job': 'Developer',
            'gender': '1',
            'internet': '3',
            'email': 'invalid_email',
            'notice': True,
            'message': 'Lorem ipsum dolor sit amet.'
        }
        form = AnketaForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_news_form_valid(self):
        form_data = {
            'title': 'Test News',
            'short_info': 'Short info',
            'text': 'Test news text',
            'images': ['image1.jpg', 'image2.jpg']
        }
        form = NewsForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_news_form_invalid(self):
        form_data = {
            'title': 'Test News',
            'short_info': '',
            'text': 'Full text of the news',
            'images': ['image1.jpg', 'image2.jpg']
        }
        form = NewsForm(data=form_data, files=form_data)
        self.assertFalse(form.is_valid())

    def test_review_form_valid(self):
        form_data = {
            'text': 'Great product!',
            'grade': '5'
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_invalid(self):
        form_data = {
            'text': '',
            'grade': '5'
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_news_comment_form_valid(self):
        form_data = {'comment': 'This is a test comment.'}
        form = NewsCommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_news_comment_form_invalid(self):
        form_data = {'comment': ''}
        form = NewsCommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        
