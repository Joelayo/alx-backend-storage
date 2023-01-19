#!/usr/bin/env python3
import requests
from functools import wraps
from cachetools import cached, TTLCache

# Create a cache with a maxsize of 100 and a ttl of 10 seconds
cache = TTLCache(maxsize=100, ttl=10)

def get_page(url: str) -> str:
    # Use the cached decorator to cache the results with the key "count:{url}"
    @cached(cache, key=f'count:{url}')
    def _get_page():
        # Use the requests module to obtain the HTML content of the URL
        response = requests.get(url)
        return response.text

    return _get_page()

# Bonus: Implement this use case with decorators
def cache_page(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        url = args[0]
        # Use the cached decorator to cache the results with the key "count:{url}"
        @cached(cache, key=f'count:{url}')
        def _get_page():
            # Call the original function
            return func(*args, **kwargs)

        return _get_page()
    return wrapper

@cache_page
def get_page_decorator(url: str) -> str:
    # Use the requests module to obtain the HTML content of the URL
    response = requests.get(url)
    return response.text