from django.contrib import admin

from ldap_view.models import LdapAttrMappings, LdapOcMappings

@admin.register(LdapOcMappings)
class LdapOcAdmin(admin.ModelAdmin):
    pass

@admin.register(LdapAttrMappings)
class LdapAttrAdmin(admin.ModelAdmin):
    list_display = [ 'object_class', 'name', 'sel_expr' ]

