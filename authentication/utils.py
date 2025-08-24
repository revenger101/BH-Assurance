from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_verification_email(user, request):
    """Send email verification email to user"""
    try:
        from .models import EmailVerificationToken
        from django.utils import timezone
        from datetime import timedelta
        
        # Create verification token
        expires_at = timezone.now() + timedelta(hours=24)  # 24 hours expiry
        verification_token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=expires_at
        )
        
        # Get current site
        current_site = get_current_site(request)
        
        # Create verification URL
        verification_url = f"http://{current_site.domain}/auth/verify-email/{verification_token.token}/"
        
        # Email context
        context = {
            'user': user,
            'verification_url': verification_url,
            'site_name': current_site.name,
            'domain': current_site.domain,
        }
        
        # Render email template
        html_message = render_to_string('authentication/emails/verify_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=f'Verify your email address - {current_site.name}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def send_password_reset_email(user, reset_token, request):
    """Send password reset email to user"""
    try:
        # Get current site
        current_site = get_current_site(request)
        
        # Create reset URL
        reset_url = f"http://{current_site.domain}/auth/reset-password/{reset_token.token}/"
        
        # Email context
        context = {
            'user': user,
            'reset_url': reset_url,
            'site_name': current_site.name,
            'domain': current_site.domain,
            'token_expires_hours': 1,
        }
        
        # Render email template
        html_message = render_to_string('authentication/emails/password_reset.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=f'Password Reset Request - {current_site.name}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False


def send_welcome_email(user, request):
    """Send welcome email to new user"""
    try:
        # Get current site
        current_site = get_current_site(request)
        
        # Email context
        context = {
            'user': user,
            'site_name': current_site.name,
            'domain': current_site.domain,
        }
        
        # Render email template
        html_message = render_to_string('authentication/emails/welcome.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=f'Welcome to {current_site.name}!',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False


def validate_user_permissions(user, required_user_type=None, required_permissions=None):
    """Validate user permissions"""
    if not user.is_authenticated:
        return False, "User not authenticated"
    
    if not user.is_active:
        return False, "User account is disabled"
    
    if required_user_type and user.user_type != required_user_type:
        return False, f"User type '{user.user_type}' not authorized. Required: '{required_user_type}'"
    
    if required_permissions:
        if not user.has_perms(required_permissions):
            return False, f"User lacks required permissions: {required_permissions}"
    
    return True, "User authorized"


def log_user_activity(user, action, ip_address=None, user_agent=None, additional_data=None):
    """Log user activity for security monitoring"""
    try:
        from .models import UserSession
        
        log_data = {
            'user_id': user.id,
            'user_email': user.email,
            'action': action,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'timestamp': timezone.now().isoformat(),
        }
        
        if additional_data:
            log_data.update(additional_data)
        
        logger.info(f"User activity: {log_data}")
        
    except Exception as e:
        logger.error(f"Failed to log user activity: {str(e)}")


def cleanup_expired_tokens():
    """Cleanup expired tokens (run this as a periodic task)"""
    from .models import PasswordResetToken, EmailVerificationToken
    from django.utils import timezone
    
    try:
        # Delete expired password reset tokens
        expired_reset_tokens = PasswordResetToken.objects.filter(
            expires_at__lt=timezone.now(),
            is_used=False
        )
        reset_count = expired_reset_tokens.count()
        expired_reset_tokens.delete()
        
        # Delete expired email verification tokens
        expired_verification_tokens = EmailVerificationToken.objects.filter(
            expires_at__lt=timezone.now(),
            is_used=False
        )
        verification_count = expired_verification_tokens.count()
        expired_verification_tokens.delete()
        
        logger.info(f"Cleaned up {reset_count} expired reset tokens and {verification_count} expired verification tokens")
        
    except Exception as e:
        logger.error(f"Failed to cleanup expired tokens: {str(e)}")


def generate_secure_token():
    """Generate a secure random token"""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))


def is_strong_password(password):
    """Check if password meets strength requirements"""
    import re
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"
