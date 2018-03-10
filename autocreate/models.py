#Cargamos los modulos restantes necesarios
from datetime import datetime
from django.db import models
from django.contrib import messages
from django.dispatch import receiver
from django.dispatch import Signal
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django_auth_ldap.backend import LDAPBackend
from cms.api import add_plugin
from cms.api import create_page
from django.utils import translation
import cms.api
import aldryn_newsblog
from django.conf import settings
from cms.models.pagemodel import Page
from cms.models.permissionmodels import GlobalPagePermission, PagePermission, PageUser, PageUserGroup


# Escucha de senhales del script
@receiver([user_logged_in, user_logged_out], sender=User)

def log_user_activity(sender, **kwargs):
	signal = kwargs.get('signal', None)
	user = kwargs.get('user', None)
	user = user.get_username()
	request = kwargs.get('request', None)
	session_key = request.session.session_key

# Dependiendo si la senhal es un inicio de sesion o un logout se haran cosas distintas
	if signal == user_logged_in:
        	action = "login"
        	messages.info(request, "Bienvenido!")
		ok = False
		for ele in aldryn_newsblog.cms_appconfig.NewsBlogConfig.objects.values_list():
			for n in range(len(ele)):
				if ele[n] == 'Blog'+str(user):
					ok = True
        	if not ok:
			creater_page(user)
	elif signal == user_logged_out:
        	action = "logout"
        	messages.info(request, 'Adios!')
         
def creater_page(user):
#Poblamos con el usuario de ldap
	usuario=LDAPBackend().populate_user(user)

#Para los problemas de traducciones
	translation.activate(settings.LANGUAGE_CODE)

#Para crear el namespace de la aplicacion a usar)
	neim = 'Blog'+str(user)
	usuario_config=aldryn_newsblog.cms_appconfig.NewsBlogConfig(namespace=neim,app_title=neim)
#Guarda la nueva aplicacion
	usuario_config.save_base()


#Pasos para la creacion de pagina
#Para indicar el padre
	parent_menu=Page.objects.filter(title_set__title='Alumnos')[0]

#Para crear la pagina
	pagina=create_page(usuario.username,'content.html','en',apphook='NewsBlogApp',apphook_namespace=usuario_config.namespace,parent=parent_menu,in_navigation=True,published=True)

#Indicar un placeholder
	place=pagina.placeholders.get(slot="content") 

#Anhadir un plugin
	add_plugin(place,'TextPlugin','en',body='Prueba')

#Configurar permisos de la pagina para un usuario
	#permisos=pagina.create_page_user(usuario.username,usuario.username,can_add_page=True,can_change_page=True,can_delete_page=True,can_add_pageuser=True,can_change_pageuser=True,can_delete_pageuser=True,grant_all=False)

#Permisos para administracion de paginas
	permisos2=cms.api.assign_user_to_page(pagina,usuario,grant_all=False)

