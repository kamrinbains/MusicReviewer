from django.shortcuts import render
from django.conf import settings
from django.shortcuts import redirect, render
import requests

# Homepage view
def index(request):
    return render(request, 'index.html')


# Contact page
def contact(request):
    if request.method == 'POST':
        return render(request, 'contact.html', {'sent': True})
    return render(request, 'contact.html', {'sent': False}) 

def about(request):
    return render(request, 'about.html')  

def review(request):
    # your GET-render logic here
    return render(request, 'review.html')

def submit_review(request):
    if request.method == 'POST':
        # TODO: grab request.POST data, save your Review model, etc.
        return redirect('review')   # back to the review page for now
    return redirect('review')

def review(request):
    album_title = request.GET.get('album', 'Unknown Album')
    album_artist = request.GET.get('artist', 'Unknown Artist')

    context = {
        'album_title': album_title,
        'album_artist': album_artist,
    }
    return render(request, 'review.html', context)

# Discogs search view
def search_discogs(request):
    query = request.GET.get('query')
    results = []

    if query:
        url = 'https://api.discogs.com/database/search'
        params = {
            'q': query,
            'token': settings.DISCOGS_TOKEN,
            'type': 'release',
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])

    return render(request, 'search_results.html', {'results': results, 'query': query})

    return render(request, 'about.html')
