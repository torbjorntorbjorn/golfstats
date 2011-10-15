from django.conf import settings


# Include DEBUG symbol in template context
# The built-in version checks against settings.INTERNAL_IPS,
# which we don't want to use.
def debug(req):
    extra = {}

    if settings.DEBUG:
        extra["DEBUG"] = True

    return extra
