"""
Custom Django context processors for injecting application information into templates.
"""
from decouple import config

def app_info(request):
    return {
        "APP_NAME": config("APP_NAME", default="PyLibrary"),
        "APP_VERSION": config("APP_VERSION", default="1.0.0"),
    }
