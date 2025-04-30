from django.shortcuts import render, redirect
import requests
from .models import Review
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        return render(request, 'contact.html', {'sent': True})
    return render(request, 'contact.html', {'sent': False})

def search_discogs(request):
    query = request.GET.get('query')
    results = []

    if query:
        url = 'https://api.discogs.com/database/search'
        params = {
            'q': query,
            'token': 'qxGXsNAYYWpkdEHvlGdGmCsDmFtHUnjJIVaCRKpz',
            'type': 'release',
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])

    return render(request, 'search_results.html', {'results': results, 'query': query})

@login_required
def review(request):
    if request.method == 'POST':
        album_title = request.POST.get('album_title')
        album_artist = request.POST.get('album_artist')
        rating = int(request.POST.get('rating'))
        review_text = request.POST.get('review_text')

        # Save review to database, tied to the logged-in user
        Review.objects.create(
            user=request.user,
            album_title=album_title,
            album_artist=album_artist,
            rating=rating,
            review_text=review_text
        )

        return render(request, 'review.html', {
            'album_title': album_title,
            'album_artist': album_artist,
            'submitted': True
        })

    album_title = request.GET.get('album', 'Unknown Album')
    album_artist = request.GET.get('artist', 'Unknown Artist')

    return render(request, 'review.html', {
        'album_title': album_title,
        'album_artist': album_artist,
        'submitted': False
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

def album_reviews(request):
    album_title = request.GET.get('album')
    album_artist = request.GET.get('artist')
    album_thumb = request.GET.get('thumb')

    if not album_title:
        return render(request, 'album_reviews.html', {'reviews': [], 'album_title': None})

    filtered_reviews = Review.objects.filter(
        album_title=album_title,
        album_artist=album_artist
    ).order_by('-submitted_at')

    context = {
        'album_title': album_title,
        'album_artist': album_artist,
        'album_thumb': album_thumb,
        'reviews': filtered_reviews
    }

    return render(request, 'album_reviews.html', context)

def reviews_list(request):
    all_reviews = Review.objects.all().order_by('-submitted_at')
    return render(request, 'reviews_list.html', {'reviews': all_reviews})

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
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        review.rating = int(request.POST.get('rating'))
        review.review_text = request.POST.get('review_text')
        review.save()
        return redirect('account')

    return render(request, 'edit_review.html', {'review': review})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('account')

@login_required
def account(request):
    return render(request, 'account.html')
