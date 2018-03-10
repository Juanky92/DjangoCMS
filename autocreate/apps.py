# myapp/apps.py
from django.apps import AppConfig

class MyAppConfig(AppConfig):

    name = 'autocreate'
    verbose_name = 'AutoCreate'

    def ready(self):
	print "pako pakito pakorro"
