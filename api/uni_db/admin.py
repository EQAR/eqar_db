from django.contrib import admin

class ModelAdmin(admin.ModelAdmin):

    def get_readonly_fields(self, req, obj):
        if obj and callable(getattr(obj, "get_readonly_fields", None)):
            readonly_fields = obj.get_readonly_fields()
        else:
            readonly_fields = []
        if getattr(self, "readonly_fields", None):
            readonly_fields = readonly_fields + self.readonly_fields
        return readonly_fields
