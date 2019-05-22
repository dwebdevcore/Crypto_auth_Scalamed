from django.contrib import admin
from authservice.models import User
from import_export.admin import ImportExportModelAdmin

class UserAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'role',
        'uuid',
        'date_joined',
    ]

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return [
                'uuid',
            ]

        return [
            'uuid',
            'date_joined',
            'password',
            '_counter',
            'secret',
            'user_permissions',
            'groups',
        ]

admin.site.register(User, UserAdmin)