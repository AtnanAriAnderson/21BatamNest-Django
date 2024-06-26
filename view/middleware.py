from typing import Any
import re

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme



def active_tab(get_response):
    def active_middleware(request):
        print(request.path_info)
        request.active_path = request.path.split("/")[-2]
        print(request.active_path)
        response = get_response(request)
        
        return response
    return active_middleware



EXEMPT_URLS = [re.compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [re.compile(url) for url in settings.LOGIN_EXEMPT_URLS]
EXEMPT_URLS.append(re.compile(r'^$'))  # Ensure root URL is exempt


class AuthMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        if not request.user.is_authenticated:
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in EXEMPT_URLS):
                redirect_to = settings.LOGIN_URL
                # 'next' variable to support redirection to attempted page after login
                if len(path) > 0 and url_has_allowed_host_and_scheme(
                    url=request.path_info, allowed_hosts=request.get_host()):
                    redirect_to = f"{settings.LOGIN_URL}?next={request.path_info}"

                return HttpResponseRedirect(redirect_to)
        return self.get_response(request)