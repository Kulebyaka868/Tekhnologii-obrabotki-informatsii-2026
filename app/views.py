"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render, redirect, Http404
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect
from app.models import Category, NewsComments, Product, Order, OrderProduct, UserProfile, Review, Image, News, NewsImages
from .forms import AnketaForm, BootstrapPasswordChangeForm, BootstrapUserCreationForm, NewsCommentForm, UserProfileForm, ReviewForm, NewsForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from collections import defaultdict
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
import json
from decimal import Decimal
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.db import connection

# ORM
def home(request):
    """Renders the home page."""
    def build_category_tree(categories, parent_id=None, parent_path=""):
        category_tree = []
        for category in categories:
            if category.parent_id == parent_id:
                path = f"{parent_path}/{category.url}" if parent_path else category.url
                children = build_category_tree(categories, parent_id=category.id, parent_path=path)
                category_data = {
                    'id': category.id,
                    'parent': category.parent_id,
                    'name': category.name,
                    'url': category.url,
                    'path': path,
                    'children': children
                }
                category_tree.append(category_data)
        return category_tree

    categories = Category.objects.all()
    category_tree = build_category_tree(categories)
    
    products = Product.objects.filter(remain__gt=0).order_by('?')[:4]
    for product in products:
        reviews = Review.objects.filter(product=product)
        images = Image.objects.filter(product=product)
        total_grade = 0
        total_reviews = len(reviews)
        for review in reviews:
            total_grade += review.grade
        if total_reviews > 0:
            product.fullGrade = round(total_grade / total_reviews, 1)
        else:
            product.fullGrade = 0
        product.totalReviews = total_reviews
        product.images = images
        print(images)
    
    avatar = None
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.filter(user=request.user).first()
        if user_profile and user_profile.avatar:
            avatar = user_profile.avatar.url

    return render(
        request,
        'app/index.html',
        {
            'title': 'Главная',
            'year': datetime.now().year,
            'products': products,
            'avatar': avatar
        }
    )

def catalog(request):
    """Renders the home page."""
    def build_category_tree(categories, parent_id=None, parent_path=""):
        category_tree = []
        for category in categories:
            if category.parent_id == parent_id:
                path = f"{parent_path}/{category.url}" if parent_path else category.url
                children = build_category_tree(categories, parent_id=category.id, parent_path=path)
                category_data = {
                    'id': category.id,
                    'parent': category.parent_id,
                    'name': category.name,
                    'url': category.url,
                    'path': path,
                    'children': children
                }
                category_tree.append(category_data)
        return category_tree

    categories = Category.objects.all()
    category_tree = build_category_tree(categories)
    
    products = Product.objects.filter(remain__gt=0).order_by('?')[:4]
    for product in products:
        reviews = Review.objects.filter(product=product)
        images = Image.objects.filter(product=product)
        total_grade = 0
        total_reviews = len(reviews)
        for review in reviews:
            total_grade += review.grade
        if total_reviews > 0:
            product.fullGrade = round(total_grade / total_reviews, 1)
        else:
            product.fullGrade = 0
        product.totalReviews = total_reviews
        product.images = images
    
    avatar = None
    if request.user.is_authenticated:
        avatar = UserProfile.objects.filter(user=request.user).first()

    return render(
        request,
        'app/catalog.html',
        {
            'title': 'Каталог',
            'year': datetime.now().year,
            'categories': category_tree,
            'products': products,
            'avatar': avatar
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    
    avatar = None
    if request.user.is_authenticated:
        avatar = UserProfile.objects.filter(user=request.user).first()

    return render(
        request,
        'app/contact.html',
        {
            'title':'Контакты',
            'message':'Страница с нашими контактами',
            'year':datetime.now().year,
            'avatar': avatar
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    
    avatar = None
    if request.user.is_authenticated:
        avatar = UserProfile.objects.filter(user=request.user).first()

    return render(
        request,
        'app/about.html',
        {
            'title':'О нас',
            'message':'Сведения о нас',
            'year':datetime.now().year,
            'avatar': avatar
        }
    )

def partners(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    
    avatar = None
    if request.user.is_authenticated:
        avatar = UserProfile.objects.filter(user=request.user).first()

    return render(
        request,
        'app/partners.html',
        {
            'title':'Партнеры',
            'year':datetime.now().year,
            'avatar':avatar
        }
    )


def anketa(request):
    assert isinstance(request, HttpRequest)
    
    gender = {'1': 'Мужчина', '2': 'Женщина'}
    internet = {'1': 'Каждый день', '2': 'Несколько раз в день', '3': 'Несколько раз в неделю', '4': 'Несколько раз в месяц'}

    if request.method == 'POST':
        form = AnketaForm(request.POST)
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'city': form.cleaned_data['city'],
                'job': form.cleaned_data['job'],
                'gender': gender.get(form.cleaned_data['gender'], ''),
                'internet': internet.get(form.cleaned_data['internet'], ''),
                'notice': 'Да' if form.cleaned_data['notice'] else 'Нет',
                'email': form.cleaned_data['email'],
                'message': form.cleaned_data['message'],
            }
        else:
            data = None
    else:
        form = AnketaForm()
        data = None
    
    return render(request, 'app/anketa.html', {'form': form, 'data': data})

def registration(request):
    """Renders the registration page."""
    if request.method == "POST":
        regform = BootstrapUserCreationForm(request.POST)
        if regform.is_valid():
            reg_f = regform.save(commit=False)
            reg_f.is_staff = False
            reg_f.is_active = True
            reg_f.is_superuser = False
            reg_f.date_joined = datetime.now()
            regform.last_login = datetime.now()
            
            regform.save()
            
            return redirect("home")
    else:
        regform = BootstrapUserCreationForm()
    assert isinstance(request, HttpRequest)
    
    avatar = None
    if request.user.is_authenticated:
        avatar = UserProfile.objects.filter(user=request.user).first()

    return render(
        request,
        "app/registration.html",
        {
            'regform': regform,
            'year': datetime.now().year,
            'title':'Регистрация',
            'avatar': avatar
        }
    )

def dynamic3(request, item1, item2, item3):
    def find_category_in_tree(category_id, tree):
        for category in tree:
            if category['id'] == category_id:
                return category
            found = find_category_in_tree(category_id, category.get('children', []))
            if found:
                return found
        return None

    def build_category_tree(categories, parent_id=None, parent_path=""):
        category_tree = []
        for category in categories:
            if category.parent_id == parent_id:
                path = f"{parent_path}/{category.url}" if parent_path else category.url
                children = build_category_tree(categories, parent_id=category.id, parent_path=path)
                category_data = {
                    'id': category.id,
                    'parent': category.parent_id,
                    'name': category.name,
                    'url': category.url,
                    'path': path,
                    'children': children
                }
                category_tree.append(category_data)
        return category_tree
    
    def get_category_ids(category_id, tree):
        ids = [category_id]
        for category in tree:
            if category['id'] == category_id:
                for child in category.get('children', []):
                    ids.extend(get_category_ids(child['id'], category.get('children', [])))
        return ids
    
    categories = Category.objects.all()
    category_tree = build_category_tree(categories)
    
    category = Category.objects.filter(url=item1).first()
    
    catalog_history = []
    
    category_data = {
        'id': 0,
        'name': "Страница не найдена",
    }
    
    title = "Ошибка 404"
    
    products = None
    paginator = None
    # Страница и сортировка
    
    page_number = request.GET.get('page')
    if not page_number:
        page_number = 1
    else:
        try:
            page_number = int(page_number)
            if page_number <= 0:
                page_number = 1
        except ValueError:
            page_number = 1

    sort_param = request.GET.get('sort')
    if not sort_param:
        sort_param = 'price_ASC'
    elif sort_param not in ['price_DESC', 'price_ASC']:
        sort_param = 'price_ASC'

    
    if category:
        catalog_history.append({
            "name": category.name,
            "path": "/catalog/" + category.url + "/"
        })
        category2 = Category.objects.filter(url=item2, parent=category.id).first()
        if (category2):
            catalog_history.append({
                "name": category2.name,
                "path": catalog_history[0]["path"] + category2.url + "/"
            })
            category3 = Category.objects.filter(url=item3, parent=category2.id).first()
            if (category3):
                category_ids = get_category_ids(category3.id, category_tree)
                # Получение продуктов
                items_per_page = 8 

                products = Product.objects.filter(category__in=category_ids)
                if sort_param == 'price_DESC':
                    products = products.order_by('-price')
                else:
                    products = products.order_by('price')

                paginator = Paginator(products, items_per_page)

                try:
                    page = paginator.page(page_number)
                except PageNotAnInteger:
                    page = paginator.page(1)
                except EmptyPage:
                    page = paginator.page(paginator.num_pages)

                page_number = page
                products = page.object_list
                for product in products:
                    reviews = Review.objects.filter(product=product)
                    images = Image.objects.filter(product=product)
                    total_grade = 0
                    total_reviews = len(reviews)
                    for review in reviews:
                        total_grade += review.grade
                    if total_reviews > 0:
                        product.fullGrade = round(total_grade / total_reviews, 1)
                    else:
                        product.fullGrade = 0
                    product.totalReviews = total_reviews
                    product.images = images

                catalog_history.append({
                    "name": category3.name,
                    "path": catalog_history[1]["path"] + category3.url + "/"
                })
                title = category3.name
                category_data = find_category_in_tree(category3.id, category_tree)
    avatar = None
    if request.user.is_authenticated:
        avatar = UserProfile.objects.filter(user=request.user).first()
    context = {
        "title": title,
        "category": category_data,
        "catalog_history": catalog_history,
        "products": products,
        "page": page_number,
        "sort": sort_param,
        "paginator": paginator,
        "avatar": avatar
    }
    return render(request, 'app/dynamic.html', context)

def dynamic2(request, item1, item2):
    def find_category_in_tree(category_id, tree):
        for category in tree:
            if category['id'] == category_id:
                return category
            found = find_category_in_tree(category_id, category.get('children', []))
            if found:
                return found
        return None

    def build_category_tree(categories, parent_id=None, parent_path=""):
        category_tree = []
        for category in categories:
            if category.parent_id == parent_id:
                path = f"{parent_path}/{category.url}" if parent_path else category.url
                children = build_category_tree(categories, parent_id=category.id, parent_path=path)
                category_data = {
                    'id': category.id,
                    'parent': category.parent_id,
                    'name': category.name,
                    'url': category.url,
                    'path': path,
                    'children': children
                }
                category_tree.append(category_data)
        return category_tree
    
    def get_category_ids(category_id, tree):
        ids = [category_id]
        for categoryParent in tree:
            for category in categoryParent["children"]: 
                if category['id'] == category_id:
                    for child in category.get('children', []):
                        ids.extend(get_category_ids(child['id'], category.get('children', [])))
        return ids

    categories = Category.objects.all()
    category_tree = build_category_tree(categories)
    
    category = Category.objects.filter(url=item1).first()
    
    catalog_history = []

    title = "Ошибка 404"
    
    category_data = {
        'id': 0,
        'name': "Страница не найдена",
    }

    products = None
    paginator = None
    # Страница и сортировка
    
    page_number = request.GET.get('page')
    if not page_number:
        page_number = 1
    else:
        try:
            page_number = int(page_number)
            if page_number <= 0:
                page_number = 1
        except ValueError:
            page_number = 1

    sort_param = request.GET.get('sort')
    if not sort_param:
        sort_param = 'price_ASC'
    elif sort_param not in ['price_DESC', 'price_ASC']:
        sort_param = 'price_ASC'

    if category:
        catalog_history.append({
            "name": category.name,
            "path": "/catalog/" + category.url + "/"
        })
        category2 = Category.objects.filter(url=item2, parent=category.id).first()
        if (category2):
            category_ids = get_category_ids(category2.id, category_tree)

            # Получение продуктов
            items_per_page = 8 

            products = Product.objects.filter(category__in=category_ids)
                
            if sort_param == 'price_DESC':
                products = products.order_by('-price')
            else:
                products = products.order_by('price')

            paginator = Paginator(products, items_per_page)

            try:
                page = paginator.page(page_number)
            except PageNotAnInteger:
                page = paginator.page(1)
            except EmptyPage:
                page = paginator.page(paginator.num_pages)

            page_number = page
            products = page.object_list
            for product in products:
                reviews = Review.objects.filter(product=product)
                images = Image.objects.filter(product=product)
                total_grade = 0
                total_reviews = len(reviews)
                for review in reviews:
                    total_grade += review.grade
                if total_reviews > 0:
                    product.fullGrade = round(total_grade / total_reviews, 1)
                else:
                    product.fullGrade = 0
                product.totalReviews = total_reviews
                product.images = images
                
            catalog_history.append({
                "name": category2.name,
                "path": catalog_history[0]["path"] + category2.url + "/"
            })
            title = category2.name
            category_data = find_category_in_tree(category2.id, category_tree)
    avatar = None
    if request.user.is_authenticated:
        avatar = UserProfile.objects.filter(user=request.user).first()
    context = {
        "title": title,
        "category": category_data,
        "catalog_history": catalog_history,
        "products": products,
        "page": page_number,
        "sort": sort_param,
        "paginator": paginator,
        "avatar": avatar
    }
    return render(request, 'app/dynamic.html', context)

def dynamic1(request, item1):
    def find_category_in_tree(category_id, tree):
        for category in tree:
            if category['id'] == category_id:
                return category
            found = find_category_in_tree(category_id, category.get('children', []))
            if found:
                return found
        return None

    def build_category_tree(categories, parent_id=None, parent_path=""):
        category_tree = []
        for category in categories:
            if category.parent_id == parent_id:
                path = f"{parent_path}/{category.url}" if parent_path else category.url
                children = build_category_tree(categories, parent_id=category.id, parent_path=path)
                category_data = {
                    'id': category.id,
                    'parent': category.parent_id,
                    'name': category.name,
                    'url': category.url,
                    'path': path,
                    'children': children
                }
                category_tree.append(category_data)
        return category_tree
    
    def get_category_ids(category_id, tree):
        ids = []
        for category in tree:
            if category['id'] == category_id:
                ids = [category_id]
                for child in category.get('children', []):
                    ids.extend(get_category_ids(child['id'], category.get('children', [])))
        return ids

    categories = Category.objects.all()
    category_tree = build_category_tree(categories)
    
    category = Category.objects.filter(url=item1).first()
    
    catalog_history = []
    
    category_data = {
        'id': 0,
        'name': "Страница не найдена",
    }
    
    title = "Ошибка 404"
    
    products = None
    paginator = None
    
    # Страница и сортировка
    
    page_number = request.GET.get('page')
    if not page_number:
        page_number = 1
    else:
        try:
            page_number = int(page_number)
            if page_number <= 0:
                page_number = 1
        except ValueError:
            page_number = 1

    sort_param = request.GET.get('sort')
    if not sort_param:
        sort_param = 'price_ASC'
    elif sort_param not in ['price_DESC', 'price_ASC']:
        sort_param = 'price_ASC'

    
    if category:
        category_ids = get_category_ids(category.id, category_tree)
        # Получение продуктов
        items_per_page = 8 

        products = Product.objects.filter(category__in=category_ids)

        if sort_param == 'price_DESC':
            products = products.order_by('-price')
        else:
            products = products.order_by('price')

        paginator = Paginator(products, items_per_page)

        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        page_number = page
        products = page.object_list
        for product in products:
            reviews = Review.objects.filter(product=product)
            images = Image.objects.filter(product=product)
            total_grade = 0
            total_reviews = len(reviews)
            for review in reviews:
                total_grade += review.grade
            if total_reviews > 0:
                product.fullGrade = round(total_grade / total_reviews, 1)
            else:
                product.fullGrade = 0
            product.totalReviews = total_reviews
            product.images = images
            
        catalog_history.append({
            "name": category.name,
            "path": "/catalog/" + category.url + "/"
        })
        title = category.name
        category_data = find_category_in_tree(category.id, category_tree)
   
    avatar = None
    if request.user.is_authenticated:
        avatar = UserProfile.objects.filter(user=request.user).first()
    
    context = {
        "title": title,
        "category": category_data,
        "catalog_history": catalog_history,
        "products": products,
        "page": page_number,
        "sort": sort_param,
        "paginator": paginator,
        "avatar": avatar
    }
    return render(request, 'app/dynamic.html', context)


def products(request, item):
    
    review_form = ReviewForm()

    product_data = {
        'id': 0,
        'name': "Страница не найдена",
    }
    
    product = Product.objects.filter(id=item).first()
    products = None
    reviews = None
    avatar = None
    userReview = None
    catalog_history = []
    reviews_with_user_info = []
    
    if product: 
        images = Image.objects.filter(product=product)
        product.images = images
        product_data = {
            'id': product.id,
            'name': product.name,
        }

        category = product.category
        category_list = []

        while category:
            category_list.insert(0, {
                "name": category.name,
                "url": category.url
            })
            category = Category.objects.filter(id=category.parent_id).first()

        category_path = "/catalog/"
        catalog_history = []

        for cat in category_list:
            category_path += f"{cat['url']}/"
            catalog_history.append({
                "name": cat["name"],
                "path": category_path
            })
            
        products = Product.objects.filter(remain__gt=0).exclude(id=product.id).order_by('?')[:4]   
        for productF in products:
            reviews = Review.objects.filter(product=productF)
            images = Image.objects.filter(product=productF)
            total_grade = 0
            total_reviews = len(reviews)
            for review in reviews:
                total_grade += review.grade
            if total_reviews > 0:
                productF.fullGrade = round(total_grade / total_reviews, 1)
            else:
                productF.fullGrade = 0
            productF.totalReviews = total_reviews
            productF.images = images
        reviews = Review.objects.filter(product=product.id)

        reviews_with_user_info = []

        for review in reviews:
            user = User.objects.filter(id=review.user_id).first()
            if user:
                user_profile = UserProfile.objects.filter(user=user).first()
                
                avatar_url = None
                if user_profile:
                    avatar_url = user_profile.avatar.url
                    
                print(review)
                print(user)
                print(avatar_url)
                reviews_with_user_info.append({
                    'id': review.id,
                    'review': review,
                    'user': user,
                    'avatar_url': avatar_url
                })

        
        if request.method == 'POST':
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                new_review = review_form.save(commit=False)
                new_review.product = product
                new_review.user = request.user
                new_review.save()
                return redirect('products', item=item)
    else:
        review_form = ReviewForm()

    if request.user.is_authenticated:
        avatar = UserProfile.objects.filter(user=request.user).first()
        userReview = Review.objects.filter(user=request.user, product=product.id).first()
        
    context = {
        "title": product_data["name"],
        "product_data": product_data,
        "product": product,
        "products": products,
        "catalog_history": catalog_history,
        "avatar": avatar,
        "reviews": reviews_with_user_info,
        "form": review_form,
        "userReview": userReview
    }
    return render(request, 'app/products.html', context)

def cart(request):
    avatar = None
    if request.user.is_authenticated:
        avatar = UserProfile.objects.filter(user=request.user).first()
    context = {
        "title": "Корзина",
        "avatar": avatar
    }
    return render(request, 'app/cart.html', context)

# ORM

@login_required
def cabinet(request):
    user_profile = UserProfile.objects.filter(user=request.user).first()
    
    if request.method == 'POST' and 'password_change' in request.POST:
        password_form = BootstrapPasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            return redirect('cabinet')
    else:
        password_form = BootstrapPasswordChangeForm(request.user)

    if request.method == 'POST' and 'profile_update' in request.POST:
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if profile_form.is_valid():
            if user_profile:
                profile = profile_form.save(commit=False)
                if 'avatar' in request.FILES:
                    profile.avatar = request.FILES['avatar']
                profile.save()
            else:
                profile = profile_form.save(commit=False)
                profile.user = request.user
                profile.save()
            return redirect('cabinet')
    else:
        profile_form = UserProfileForm(instance=user_profile)

    active_orders = Order.objects.filter(user=request.user)
    user_reviews = Review.objects.filter(user=request.user)

    for order in active_orders:
        order.items = OrderProduct.objects.filter(order=order)
        order.total_cost = sum(item.price * item.count for item in order.items)
        
    context = {
        "title": "Кабинет",
        "active_orders": active_orders,
        "form": password_form,
        "profile_form": profile_form,
        "avatar": user_profile if user_profile and user_profile.avatar else None,
        "reviews": user_reviews,
        "user_groups": request.user.groups.all()
    }
    return render(request, 'app/cabinet.html', context)

# SQL

# @login_required
# def cabinet(request):
#     if request.method == 'POST' and 'password_change' in request.POST:
#         password_form = BootstrapPasswordChangeForm(request.user, request.POST)
#         if password_form.is_valid():
#             user = password_form.save()
#             update_session_auth_hash(request, user)
#             return redirect('cabinet')
#     else:
#         password_form = BootstrapPasswordChangeForm(request.user)

#     if request.method == 'POST' and 'avatar_upload' in request.POST:  
#         avatar_form = UserProfileForm(request.POST, request.FILES)
#         if avatar_form.is_valid() and 'avatar_upload' in request.POST:
#             avatar_data = avatar_form.cleaned_data['avatar']
#             avatar_path = avatar_data.name 

#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT id FROM app_userprofile WHERE user_id = %s
#                 """, [request.user.id])
#                 user_profile = cursor.fetchone()
                
#                 if user_profile:
#                     cursor.execute("""
#                         UPDATE app_userprofile SET avatar = %s WHERE user_id = %s
#                     """, [avatar_path, request.user.id])
#                 else:
#                     cursor.execute("""
#                         INSERT INTO app_userprofile (user_id, avatar)
#                         VALUES (%s, %s)
#                     """, [request.user.id, avatar_path])

#             handle_uploaded_file(request.FILES['avatar'], avatar_path)
#     else:
#         avatar_form = UserProfileForm()

#     active_orders = Order.objects.filter(user=request.user)
#     user_reviews = Review.objects.filter(user=request.user)

#     for order in active_orders:
#         order.items = OrderProduct.objects.filter(order=order)
#         order.total_cost = sum(item.price * item.count for item in order.items)
        
#     avatar = None
#     if request.user.is_authenticated:
#         avatar = UserProfile.objects.filter(user=request.user).first()
        
#     context = {
#         "title": "Кабинет",
#         "active_orders": active_orders,
#         "form": password_form,
#         "avatar_form": avatar_form,
#         "avatar": avatar,
#         "reviews": user_reviews
#     }
#     return render(request, 'app/cabinet.html', context)

# def handle_uploaded_file(file, filename):
#     with open(f'media/{filename}', 'wb+') as destination:
#         for chunk in file.chunks():
#             destination.write(chunk)

# ORM

def create_order(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            cart_items = json.loads(request.body)
            order = Order.objects.create(user=request.user)
            print(cart_items)
            for item in cart_items["cartItems"]:
                product_id = item['id']
                quantity = item['quantity']
                price = item['price']

                price = Decimal(item['price'].replace(',', '.'))

                order_product = OrderProduct.objects.create(order=order, product_id=product_id, count=quantity, price=price)

            request.session['cartItems'] = []

            return JsonResponse({'message': 'Заказ успешно оформлен.'}, status=201)
        else:
            return JsonResponse({'error': 'Пользователь не аутентифицирован.'}, status=401)
    else:
        return JsonResponse({'error': 'Метод запроса должен быть POST.'}, status=405)
    

@require_POST
def delete_order(request, order_id):
    if request.user.is_authenticated:
        try:
            order = Order.objects.get(pk=order_id, user=request.user)
            order.delete()
            return JsonResponse({'message': 'Заказ успешно удален.'}, status=200)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Указанный заказ не существует или не принадлежит текущему пользователю.'}, status=404)
    else:
        return JsonResponse({'error': 'Пользователь не аутентифицирован.'}, status=401)
    
@require_POST
def delete_comment(request, comment_id):
    if request.user.is_authenticated:
        try:
            comment = NewsComments.objects.get(pk=comment_id, user=request.user)
            comment.delete()
            return JsonResponse({'message': 'Комментарий успешно удален.'}, status=200)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Указанный комментарий не существует или не принадлежит текущему пользователю.'}, status=404)
    else:
        return JsonResponse({'error': 'Пользователь не аутентифицирован.'}, status=401)
    
@require_POST
def delete_review(request, review_id):
    if request.user.is_authenticated:
        try:
            review = Review.objects.get(pk=review_id, user=request.user)
            review.delete()
            return JsonResponse({'message': 'Отзыв успешно удален.'}, status=200)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Отзыв не существует или не принадлежит текущему пользователю.'}, status=404)
    else:
        return JsonResponse({'error': 'Пользователь не аутентифицирован.'}, status=401)
    

def news(request):
    avatar = None
    if request.user.is_authenticated:
        avatar = UserProfile.objects.filter(user=request.user).first()

    news = News.objects.all()
    for snews in news:
        images = NewsImages.objects.filter(news=snews)
        snews.images = images
        
    context = {
        "title": "Новости",
        "avatar": avatar,
        "news": news
    }
    return render(request, 'app/news.html', context)

def newsdetails(request, item):
   
    avatar = None
    
    news_data = {
        "title": "Страница не найдена",
        "news":{"name": "Страница не найдена"},
        "id": 0
    }

    if request.user.is_authenticated:
        avatar = UserProfile.objects.filter(user=request.user).first()
        news_data = {
            "title": "Страница не найдена",
            "id": 0,
            "avatar": avatar
        }
    
    news = News.objects.filter(id=item).first()
    
    if news:
        images = NewsImages.objects.filter(news=news)
        comments = NewsComments.objects.filter(news=news)
        all_news = News.objects.exclude(id=news.id)[:4]
        for snews in all_news:
            images1 = NewsImages.objects.filter(news=snews)
            snews.images = images1
        news.images = images
        comment_form = NewsCommentForm()
        news_data = {
            "title": news.title,
            "id": news.id,
            "news": news,
            "all_news": all_news,
            "comments": comments,
            "comment_form": comment_form
        }


    context = news_data
    
    if request.method == 'POST':
        comment_form = NewsCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.news = news
            comment.user = request.user
            comment.save()
            url = reverse('newsdetails', kwargs={'item': item}) + '#comments'
            return HttpResponseRedirect(url)
        else:
            comment_form = NewsCommentForm()
    return render(request, 'app/newsdetails.html', context)

@login_required
def addnews(request):
    avatar = None
    if request.user.is_authenticated:
        avatar = UserProfile.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news_instance = form.save(commit=False)
            news_instance.user = request.user
            news_instance.save()

            for file in request.FILES.getlist('images'):
                news_image = NewsImages(news=news_instance, path=file)
                news_image.save()
                
            news_id = news_instance.pk
            
            redirect_url = f'/news/{news_id}/'
            return redirect(redirect_url)
    else:
        form = NewsForm()
    
    context = {
        "title": "Создание новости",
        "avatar": avatar,
        "form": form 
    }
    return render(request, 'app/addnews.html', context)


def error_404(request, exception):
    return render(request, 'app/404.html', status=404)

def sample_view(request):
    return render(request, 'app/sample.html')