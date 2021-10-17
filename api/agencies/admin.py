from django import forms
from django.contrib import admin
from django.db.models import Q

from agencies.models import RegisteredAgency, Applications, ApplicationRole, ApplicationInterest, ApplicationClarification, ChangeReport, Complaint, AgencyUpdate
from contacts.models import Contact, Organisation, ContactOrganisation

class RoleInline(admin.TabularInline):
    model = ApplicationRole
    autocomplete_fields = [ 'contact' ]
    extra = 0
    readonly_fields = [ 'mtime' ]

class ClarificationInline(admin.StackedInline):
    model = ApplicationClarification
    autocomplete_fields = [ 'recipientOrg', 'recipientContact' ]
    extra = 0
    readonly_fields = [ 'mtime' ]

class InterestInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact'].queryset = Contact.objects.filter(
            Q(contactorganisation__in=ContactOrganisation.objects.filter(organisation=Organisation.objects.get(acronym='** EQAR **'), function__startswith='RC')) |
            (Q(pk=self.instance.contact_id) if self.instance.contact_id else Q())
        )

class InterestInline(admin.TabularInline):
    model = ApplicationInterest
    form = InterestInlineForm
    extra = 0
    readonly_fields = [ 'mtime' ]

class ApplicationAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'rapporteur1' in self.fields:
            self.fields['rapporteur1'].queryset = Contact.objects.filter(
                Q(contactorganisation__in=ContactOrganisation.objects.filter(organisation=Organisation.objects.get(acronym='** EQAR **'), function__startswith='RC')) |
                (Q(pk=self.instance.rapporteur1.pk) if self.instance.rapporteur1 else Q())
            )
        if 'rapporteur2' in self.fields:
            self.fields['rapporteur2'].queryset = Contact.objects.filter(
                Q(contactorganisation__in=ContactOrganisation.objects.filter(organisation=Organisation.objects.get(acronym='** EQAR **'), function__startswith='RC')) |
                (Q(pk=self.instance.rapporteur2.pk) if self.instance.rapporteur2 else Q())
            )
        if 'rapporteur3' in self.fields:
            self.fields['rapporteur3'].queryset = Contact.objects.filter(
                Q(contactorganisation__in=ContactOrganisation.objects.filter(organisation=Organisation.objects.get(acronym='** EQAR **'), function__startswith='RC')) |
                (Q(pk=self.instance.rapporteur3.pk) if self.instance.rapporteur3 else Q())
            )
        if 'secretary' in self.fields:
            self.fields['secretary'].queryset = Contact.objects.filter(
                Q(contactorganisation__in=ContactOrganisation.objects.filter(organisation=Organisation.objects.get(acronym='** EQAR **'), function__startswith='SEC')) |
                (Q(pk=self.instance.secretary.pk) if self.instance.secretary else Q())
            )

@admin.register(Applications)
class ApplicationAdmin(admin.ModelAdmin):
    form = ApplicationAdminForm
    list_display = [ 'id', 'agency', 'type', 'submitDate', 'stage', 'result' ]
    list_filter = [ 'type', 'submitDate', 'stage', 'result' ]
    search_fields = [ 'agency__shortname', 'agency__organisation__longname' ]
    inlines = [RoleInline, InterestInline, ClarificationInline]
    readonly_fields = [ 'mtime' ]

@admin.register(AgencyUpdate)
class UpdateAdmin(admin.ModelAdmin):
    list_display = [ 'agency', 'type', 'year', 'country', 'source' ]
    list_filter = [ 'agency', 'type', 'year', 'country', 'source' ]
    search_fields = [ 'agency__shortname', 'agency__organisation__longname', 'country__name', 'country__iso2', 'country__iso3' ]
    readonly_fields = [ 'mtime' ]

@admin.register(RegisteredAgency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = [ 'shortname', 'deqarId', 'baseCountry', 'registered', 'registeredSince', 'validUntil' ]
    list_filter = [ 'registered', 'registeredSince', 'validUntil' ]
    search_fields = [ 'shortname', 'organisation__longname', 'baseCountry__name', 'baseCountry__iso2', 'baseCountry__iso3' ]
    readonly_fields = [ 'register_url', 'mtime' ]

@admin.register(ChangeReport)
class ChangeReportAdmin(admin.ModelAdmin):
    list_display = [ 'id', 'agency', 'submitDate', 'stage', 'result' ]
    list_filter = [ 'submitDate', 'stage', 'result' ]
    search_fields = [ 'agency__shortname', 'agency__organisation__longname' ]
    readonly_fields = [ 'mtime' ]

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = [ 'id', 'agency', 'submitDate', 'stage', 'result' ]
    list_filter = [ 'submitDate', 'stage', 'result' ]
    search_fields = [ 'agency__shortname', 'agency__organisation__longname' ]
    readonly_fields = [ 'mtime' ]

