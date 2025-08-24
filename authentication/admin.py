from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, UserSession, PasswordResetToken, EmailVerificationToken


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom user admin"""

    list_display = [
        'email', 'name', 'user_type', 'is_active',
        'is_verified', 'date_joined', 'last_login'
    ]
    list_filter = [
        'user_type', 'is_active', 'is_verified',
        'is_staff', 'date_joined'
    ]
    search_fields = ['email', 'name', 'phone_number']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal Info', {
            'fields': ('name', 'phone_number', 'profile_picture', 'bio')
        }),
        ('Permissions', {
            'fields': (
                'user_type', 'is_active', 'is_staff',
                'is_superuser', 'is_verified', 'groups', 'user_permissions'
            )
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'name', 'phone_number', 'user_type',
                'password1', 'password2', 'is_active', 'is_staff'
            ),
        }),
    )

    readonly_fields = ['date_joined', 'last_login', 'updated_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """User session admin"""

    list_display = [
        'user', 'ip_address', 'is_active',
        'created_at', 'last_activity'
    ]
    list_filter = ['is_active', 'created_at', 'last_activity']
    search_fields = ['user__email', 'user__name', 'ip_address']
    readonly_fields = ['session_key', 'created_at', 'last_activity']
    ordering = ['-last_activity']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Password reset token admin"""

    list_display = [
        'user', 'token', 'created_at',
        'expires_at', 'is_used', 'is_expired_display'
    ]
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__email', 'user__name']
    readonly_fields = ['token', 'created_at', 'is_expired_display']
    ordering = ['-created_at']

    def is_expired_display(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Valid</span>')
    is_expired_display.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Email verification token admin"""

    list_display = [
        'user', 'token', 'created_at',
        'expires_at', 'is_used', 'is_expired_display'
    ]
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__email', 'user__name']
    readonly_fields = ['token', 'created_at', 'is_expired_display']
    ordering = ['-created_at']

    def is_expired_display(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Valid</span>')
    is_expired_display.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
