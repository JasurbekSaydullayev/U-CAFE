from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'full_name', 'is_active', 'user_type')
    list_editable = ('is_active', 'user_type')
