from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.core.mail import send_mail
from django.contrib.auth import logout

from django.core.paginator import Paginator

from .models import Review
from django.db.models import Avg

import requests
import random


def index(request):
    genres = ["rock", "metal", "punk", "jazz", "pop", "hip-hop", "electronic"]
    featured_albums = []

    for _ in range(3):
        genre = random.choice(genres)
        params = {
            'token': 'qxGXsNAYYWpkdEHvlGdGmCsDmFtHUnjJIVaCRKpz',
            'genre': genre,
            'type': 'release',
            'per_page': 50,
            'page': random.randint(1, 10)
        }
        response = requests.get('https://api.discogs.com/database/search', params=params)
        results = response.json().get('results', [])
        if results:
            album = random.choice(results)
            featured_albums.append({
                'title': album.get('title'),
                'thumb': album.get('thumb'),
                'genre': album.get('genre', ['Unknown'])[0],
                'description': f"A featured release in {genre}.",
            })

    return render(request, 'index.html', {'featured_albums': featured_albums})

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email') or 'anonymous@liner-notes.com'
        message = request.POST.get('message')

        full_message = f"From: {name}\nEmail: {email}\n\nMessage:\n{message}"

        send_mail(
            subject=f'New Contact Message from {name}',
            message=full_message,
            from_email='linernotecontact@gmail.com',  # matches your EMAIL_HOST_USER
            recipient_list=['linernotecontact@gmail.com'],
        )

        return render(request, 'contact.html', {'sent': True})

    return render(request, 'contact.html', {'sent': False})

def search_discogs(request):
    query = request.GET.get('query', '')
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 50)

    results = []
    pagination = {}

    if query:
        url = 'https://api.discogs.com/database/search'
        params = {
            'q': query,
            'token': 'qxGXsNAYYWpkdEHvlGdGmCsDmFtHUnjJIVaCRKpz',
            'type': 'release',
            'page': page,
            'per_page': per_page,
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            raw = data.get('results', [])
            pagination = data.get('pagination', {})
            for item in raw:
                title = item.get('title', '')
                if ' - ' in title:
                    artist, album = title.split(' - ', 1)
                else:
                    artist, album = '', title
                results.append({
                    'id': item['id'],
                    'artist': artist,
                    'album_title': album,
                    'thumb': item.get('thumb'),
                    'resource_url': item.get('resource_url'),
                })


    genres = ["rock", "metal", "punk", "jazz", "pop", "hip-hop", "electronic"]
    featured_albums = []
    attempts = 0
    while len(featured_albums) < 3 and attempts < 10:
        genre = random.choice(genres)
        params = {
            'token': 'qxGXsNAYYWpkdEHvlGdGmCsDmFtHUnjJIVaCRKpz',
            'genre': genre,
            'type': 'release',
            'per_page': 50,
            'page': random.randint(1, 10)
        }
        featured_response = requests.get('https://api.discogs.com/database/search', params=params)
        genre_results = featured_response.json().get('results', [])
        if genre_results:
            album = random.choice(genre_results)
            featured_albums.append({
                'title': album.get('title'),
                'thumb': album.get('thumb'),
                'genre': album.get('genre', [genre])[0],
                'description': f"A featured release in {genre}.",
            })

    return render(request, 'search_results.html', {

        'results': results,
        'query': query,
        'pagination': pagination,
        'featured_albums': featured_albums,
    })

@login_required
def review(request):
    album_title  = request.GET.get('album_title',  'Unknown Album')
    album_artist = request.GET.get('album_artist', 'Unknown Artist')
    thumb = request.GET.get('thumb', '')

    if request.method == 'POST':
        album_title = request.POST.get('album_title')
        album_artist = request.POST.get('album_artist')
        thumb_url = request.POST.get('thumb_url', '')
        rating = int(request.POST.get('rating'))
        review_text = request.POST.get('review_text')

        Review.objects.create(
            user=request.user,
            album_title=album_title,
            album_artist=album_artist,
            thumb_url=thumb_url,
            rating=rating,
            review_text=review_text
        )

        return redirect('account')

    return render(request, 'review.html', {
        'album_title': album_title,
        'album_artist': album_artist,
        'thumb': thumb,
    })

@login_required
def account(request):
    user_reviews = Review.objects.filter(user=request.user).order_by('-submitted_at')
    review_count = user_reviews.count()

    top_review = user_reviews.order_by('-rating').first()

    context = {
        'user_reviews': user_reviews,
        'review_count': review_count,
        'top_review': top_review,
    }

    return render(request, 'account.html', context)



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('account')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user
    =request.user)
    choices = [5, 4, 3, 2, 1]

    if request.method == 'POST':
        review.rating = int(request.POST.get('rating'))
        review.review_text = request.POST.get('review_text')
        review.save()
        return redirect('account')

    return render(request, 'edit_review.html', {'review': review, 'rating_choices': choices,})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        review.delete()
        return redirect('account')
    return render(request, 'confirm_delete.html', {'review': review})


@login_required
def album_reviews(request):
    album_title  = request.GET.get('album_title', '')
    album_artist = request.GET.get('album_artist', '')
    thumb = request.GET.get('thumb', '')

    reviews_qs = Review.objects.filter(
        album_title=album_title,
        album_artist=album_artist
    ).order_by('-submitted_at')

    avg = reviews_qs.aggregate(average=Avg('rating'))['average'] or 0
    avg = round(avg, 1)

    paginator = Paginator(reviews_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'album_reviews.html', {
        'album_title': album_title,
        'album_artist': album_artist,
        'thumb': thumb,
        'page_obj': page_obj,
        'average_rating': avg,
    })

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        return redirect('index')  # or 'login' if you prefer
    return redirect('account')