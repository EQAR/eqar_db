from django.contrib import admin

from uni_db.admin import ModelAdmin

from members.models import Member, Invoice

class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 0
    readonly_fields = [ 'mtime' ]

class MemberAdmin(ModelAdmin):
    inlines = [InvoiceInline]
    list_display = [ 'name', 'id', 'cat', 'votes' ]
    readonly_fields = [ 'mtime' ]

admin.site.register(Member, MemberAdmin)

