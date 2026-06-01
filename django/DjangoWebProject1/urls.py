"""
Definition of urls for DjangoWebProject1.
"""

from datetime import datetime
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views
from django.conf.urls import handler404
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('partners/', views.partners, name='partners'),
    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Вход',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(template_name='app/login.html', next_page='/'), name='logout'),
    path('admin/', admin.site.urls),
    path('anketa/', views.anketa, name='anketa'),
    path('registration/', views.registration, name='registration'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<str:item1>/<str:item2>/<str:item3>/', views.dynamic3, name='dynamic3'),
    path('catalog/<str:item1>/<str:item2>/', views.dynamic2, name='dynamic2'),
    path('catalog/<str:item1>/', views.dynamic1, name='dynamic1'),
    path('products/<int:item>/', views.products, name='products'),
    path('cart/', views.cart, name='cart'),
    path('cabinet/', views.cabinet, name='cabinet'),
    path('news/', views.news, name='news'),
    path('news/<int:item>/', views.newsdetails, name='newsdetails'),
    path('addnews/', views.addnews, name='addnews'),
    
    path('create_order/', views.create_order, name='create_order'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('sample/', views.sample_view, name='sample'),
]

handler404 = views.error_404

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()