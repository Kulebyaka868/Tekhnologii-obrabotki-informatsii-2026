"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from django.core.files.images import get_image_dimensions
from .models import NewsComments, UserProfile, Review, News, NewsImages

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result   

class UserProfileForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'custom-input',
            'placeholder': '+7 (999) 999-99-99'
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'custom-input',
            'rows': 3,
            'placeholder': 'Введите адрес доставки'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = ['avatar', 'phone', 'address']
        labels = {
            'avatar': '',
            'phone': 'Номер телефона',
            'address': 'Адрес доставки'
        }
        
    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']
        if avatar:
            try:
                main, sub = avatar.content_type.split('/')
                if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
                    raise forms.ValidationError('Пожалуйста, используйте изображение в формате JPEG, GIF или PNG.')
            except AttributeError:
                pass
        return avatar
        
class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': ' custom-input',
                                   'placeholder': 'Имя пользователя'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'custom-input',
                                   'placeholder':'Пароль'}))
    
class BootstrapUserCreationForm(UserCreationForm):
    """User creation form which uses bootstrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'custom-input',
                                   'placeholder': 'Имя пользователя'}))
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput({
                                    'class': 'custom-input',
                                    'placeholder': 'Пароль'}))
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput({
                                    'class': 'custom-input',
                                    'placeholder': 'Подтверждение пароля'}))

class BootstrapPasswordChangeForm(PasswordChangeForm):
    """Password change form which uses bootstrap CSS."""
    old_password = forms.CharField(label=_("Old password"),
                                   widget=forms.PasswordInput({
                                       'class': 'custom-input',
                                       'placeholder': 'Старый пароль'}))
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput({
                                        'class': 'custom-input',
                                        'placeholder': 'Новый пароль'}))
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput({
                                        'class': 'custom-input',
                                        'placeholder': 'Подтверждение нового пароля'}))
    
class AnketaForm(forms.Form):
    name = forms.CharField(label='Имя', max_length=100)
    city = forms.CharField(label='Город', max_length=100)
    job = forms.CharField(label='Специальность', max_length=100)
    gender_choices = [
        ('1', 'Мужской'),
        ('2', 'Женский'),
    ]
    gender = forms.ChoiceField(label='Пол', choices=gender_choices, initial='male', widget=forms.RadioSelect)
    internet_choices = [
        ('1', 'Редко'),
        ('2', 'Иногда'),
        ('3', 'Часто'),
    ]
    internet = forms.ChoiceField(label='Частота использования интернета', choices=internet_choices, initial='often')
    email = forms.EmailField(label='E-mail', max_length=100)
    notice = forms.BooleanField(label='Получать новости сайта', required=False)
    message = forms.CharField(label='Короткое резюме', widget=forms.Textarea)
    
class NewsForm(forms.ModelForm):
    images = MultipleFileField(label='Изображения')

    class Meta:
        model = News
        fields = ['title', 'short_info', 'text', 'images']
        labels = {
            'title': 'Заголовок',
            'short_info': 'Краткая информация',
            'text': 'Текст новости',
            'images': 'Изображения',
        }

    def __init__(self, *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'custom-input'})
        self.fields['short_info'].widget.attrs.update({'style': 'height: 50px;', 'maxlength': '100'}) 
        self.fields['text'].widget.attrs.update({'style': 'height: 300px;'})

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'grade']
        labels = {
            'text': 'Текст отзыва',
            'grade': 'Оценка',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }

class NewsCommentForm(forms.ModelForm):
    class Meta:
        model = NewsComments
        fields = ['comment']
        labels = {
            'comment': 'Оставьте комментарий',
        }

    def __init__(self, *args, **kwargs):
        super(NewsCommentForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 40})
