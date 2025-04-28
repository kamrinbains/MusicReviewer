from django.shortcuts import render
from django.conf import settings
import requests

# Homepage view
def index(request):
    return render(request, 'index.html')

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
