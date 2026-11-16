from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods
from django.middleware.csrf import get_token
from integration import policy_adapter as policy
from .models import Consent


def reply(value, status=200):
    response = JsonResponse(value, safe=False, status=status)
    response['Cache-Control'] = 'no-store'
    return response


def profile(user):
    return {'first_name':user.first_name, 'last_name':user.last_name, 'email':user.email, 'date_joined':user.date_joined.isoformat()}


@login_required
@require_GET
@ensure_csrf_cookie
def page(request):
    response = render(request, 'privacy.html')
    response['Cache-Control'] = 'no-store'
    return response


@require_GET
@ensure_csrf_cookie
def csrf(request):
    if not request.user.is_authenticated:
        return reply({'error':'Please sign in'}, 401)
    return reply({'token':get_token(request)})


def read(request, operation, write=False):
    if request.content_type != 'application/json':
        return None, reply({'error':'JSON content type required'}, 415)
    try:
        if int(request.META.get('CONTENT_LENGTH') or 0) > 16384:
            raise OverflowError('Request too large')
        value = policy.validate(operation, policy.decode(request.body), ('first_name','last_name','email','date_joined'), ('first_name','last_name','email'), write)
    except OverflowError as exc:
        return None, reply({'error':str(exc)}, 413)
    except (policy.InvalidInput, ValueError) as exc:
        return None, reply({'error':str(exc)}, 400)
    return value, None


@require_http_methods(['PATCH', 'POST'])
def consent(request):
    if request.method == 'POST':
        return evaluate(request, 'consent')
    if not request.user.is_authenticated or not request.user.is_active:
        return reply({'error':'Please sign in'}, 401)
    value, error = read(request, 'consent', True)
    if error is not None:
        return error
    Consent.objects.update_or_create(user=request.user, defaults=value)
    return reply(value)


@require_http_methods(['POST'])
def evaluate(request, operation):
    if not request.user.is_authenticated or not request.user.is_active:
        return reply({'error':'Please sign in'}, 401)
    value, error = read(request, operation)
    if error is not None:
        return error
    if operation == 'breach' and not (request.user.is_staff and request.user.is_superuser):
        return reply({'error':'Administrator access required'}, 403)
    saved = Consent.objects.filter(user=request.user).first()
    saved_value = {'value':saved.value, 'withdrawn':saved.withdrawn} if saved else None
    try:
        result = policy.evaluate(operation, profile(request.user), str(request.user.pk), saved_value, value)
    except Exception:
        return reply({'error':'OPA evaluation failed'}, 502)
    return reply(result)
