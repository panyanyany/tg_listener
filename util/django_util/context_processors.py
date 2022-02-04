from django.conf import settings as sett


# make settings object accessible in templates
def settings(request):
    return {'SETTINGS': sett}
