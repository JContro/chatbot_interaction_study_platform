from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, InstrumentResponse


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin configuration for the User model.
    """
    list_display = ('email', 'is_email_verified',
                    'is_active', 'is_staff', 'date_joined',
                    'baseline_status', 'baseline_started_at',
                    'baseline_completed_at', 'baseline_failed_item_index',
                    'baseline_failed_keystroke')
    list_filter = ('is_active', 'is_staff',
                   'is_email_verified', 'is_superuser', 'baseline_status')
    search_fields = ('email',)
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Email verification', {
         'fields': ('is_email_verified', 'email_verified_at')}),
        ('Baseline psych battery', {
         'fields': ('baseline_status', 'baseline_started_at',
                    'baseline_completed_at', 'baseline_failed_item_index',
                    'baseline_failed_keystroke')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


@admin.register(InstrumentResponse)
class InstrumentResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'instrument_slug', 'item_index', 'value', 'updated_at')
    list_filter = ('instrument_slug',)
    search_fields = ('user__email',)
    list_select_related = ('user',)
