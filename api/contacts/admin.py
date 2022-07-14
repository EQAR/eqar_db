from django import forms
from django.contrib import admin
from django.db.models import Q

from uni_db.admin import ModelAdmin

from contacts.models import Contact, Organisation, Country, OctopusAccount, Role, DeqarPartner, DeqarConnectPartner, ContactOrganisation

"""
Forms: mainly used to limit certain select boxes to own contacts
"""
class OctopusForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cid'].queryset = Contact.objects.filter(
            (Q(organisation=self.instance.organisation) if self.instance.organisation_id else Q()) |
            (Q(pk=self.instance.cid_id) if self.instance.cid_id else Q())
        )

class DeqarConnectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact_technical'].queryset = Contact.objects.filter(
            (Q(organisation=self.instance.organisation) if self.instance.organisation_id else Q()) |
            (Q(pk=self.instance.contact_technical_id) if self.instance.contact_technical_id else Q())
        )
        self.fields['contact_admin'].queryset = Contact.objects.filter(
            (Q(organisation=self.instance.organisation) if self.instance.organisation_id else Q()) |
            (Q(pk=self.instance.contact_admin_id) if self.instance.contact_admin_id else Q())
        )

class DeqarForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manager'].queryset = Contact.objects.filter(
            (Q(organisation=self.instance.organisation) if self.instance.organisation_id else Q()) |
            (Q(pk=self.instance.manager_id) if self.instance.manager_id else Q())
        )
        self.fields['technician'].queryset = Contact.objects.filter(
            (Q(organisation=self.instance.organisation) if self.instance.organisation_id else Q()) |
            (Q(pk=self.instance.technician_id) if self.instance.technician_id else Q())
        )
        self.fields['signatory'].queryset = Contact.objects.filter(
            (Q(organisation=self.instance.organisation) if self.instance.organisation_id else Q()) |
            (Q(pk=self.instance.signatory_id) if self.instance.signatory_id else Q())
        )


"""
Inline widgets
"""
class OctopusInline(admin.StackedInline):
    model = OctopusAccount
    form = OctopusForm
    extra = 0
    readonly_fields = [ 'mtime' ]

class ContactOrganisationInline(admin.TabularInline):
    model = ContactOrganisation
    autocomplete_fields = [ 'contact', 'organisation' ]
    extra = 0
    readonly_fields = [ 'mtime' ]

class DeqarConnectInline(admin.StackedInline):
    model = DeqarConnectPartner
    form = DeqarConnectForm
    readonly_fields = [ 'pic', 'mtime' ]
    extra = 0

class DeqarInline(admin.StackedInline):
    model = DeqarPartner
    form = DeqarForm
    readonly_fields = [ 'pic', 'pic_name' ]
    extra = 0

"""
Main admin modules
"""

@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    inlines = [ContactOrganisationInline]
    search_fields = [ 'firstName', 'lastName', 'email' ]
    readonly_fields = [ 'mtime' ]

@admin.register(Organisation)
class OrganisationAdmin(ModelAdmin):
    inlines = [ContactOrganisationInline, OctopusInline, DeqarInline, DeqarConnectInline]
    search_fields = [ 'longname', 'acronym', 'country__name', 'city' ]
    readonly_fields = [ 'mtime' ]

@admin.register(Country)
class CountryAdmin(ModelAdmin):
    search_fields = [ 'name', 'name_local' ]
    
@admin.register(DeqarPartner)
class DeqarPartnerAdmin(ModelAdmin):
    readonly_fields = [ 'mtime', 'pic', 'pic_name' ]
    form = DeqarForm

@admin.register(DeqarConnectPartner)
class DeqarConnectAdmin(ModelAdmin):
    list_display = [ 'organisation', 'id', 'type' ]
    list_filter = [ 'type' ]
    readonly_fields = [ 'mtime', 'pic' ]
    form = DeqarConnectForm

admin.site.register(Role)

