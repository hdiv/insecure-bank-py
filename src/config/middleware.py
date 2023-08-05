from django.http import HttpResponseRedirect


class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        login_page = request.path.startswith("/login")
        principal = request.user
        if principal.is_authenticated or login_page:
            return self.get_response(request)
        else:
            return HttpResponseRedirect("/login")
