from django.contrib import admin
from .models import UserProfile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm

    model = UserProfile

    list_display = ('email','phone_number', 'is_active',
                    'is_staff', 'is_superuser', 'last_login','is_active')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('first_name','last_name', 'email','phone_number', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active','is_superuser','email_verified','otp', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name','last_name', 'email','phone_number', 'password1', 'password2', 'is_staff', 'is_active','is_superuser')}
        ),
    )
    search_fields = ('email','phone_number')
    ordering = ('email','phone_number','last_login')


admin.site.register(UserProfile, CustomUserAdmin)