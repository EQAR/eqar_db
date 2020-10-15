from django.contrib import admin

from members.models import Member, Invoice

class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 0
    readonly_fields = [ 'mtime' ]

class MemberAdmin(admin.ModelAdmin):
    inlines = [InvoiceInline]
    list_display = [ 'name', 'id', 'cat', 'votes' ]
    readonly_fields = [ 'mtime' ]

admin.site.register(Member, MemberAdmin)

