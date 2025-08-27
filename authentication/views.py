from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import uuid

from .models import CustomUser, UserSession, PasswordResetToken, EmailVerificationToken
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserSessionSerializer
)
from .utils import get_client_ip, send_verification_email, send_password_reset_email


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """Register a new user"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"Registration attempt with data: {request.data}")
    serializer = UserRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        # Create authentication token
        token, created = Token.objects.get_or_create(user=user)

        # Create user session
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        UserSession.objects.create(
            user=user,
            session_key=session_key,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # Send verification email (optional)
        # send_verification_email(user, request)

        return Response({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'user': UserProfileSerializer(user).data,
                'token': token.key
            }
        }, status=status.HTTP_201_CREATED)

    logger.error(f"Registration validation failed: {serializer.errors}")
    return Response({
        'success': False,
        'message': 'Registration failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    """Login user"""
    serializer = UserLoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data['user']

        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        # Create or get authentication token
        token, created = Token.objects.get_or_create(user=user)

        # Create user session
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        # Deactivate old sessions (optional - for single session per user)
        # UserSession.objects.filter(user=user, is_active=True).update(is_active=False)

        # Create or update user session
        user_session, created = UserSession.objects.get_or_create(
            session_key=session_key,
            defaults={
                'user': user,
                'ip_address': get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'is_active': True
            }
        )
        if not created:
            # Update existing session
            user_session.user = user
            user_session.ip_address = get_client_ip(request)
            user_session.user_agent = request.META.get('HTTP_USER_AGENT', '')
            user_session.is_active = True
            user_session.save()

        # Django login
        login(request, user)

        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': UserProfileSerializer(user).data,
                'token': token.key
            }
        }, status=status.HTTP_200_OK)

    return Response({
        'success': False,
        'message': 'Login failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    """Logout user"""
    try:
        # Delete authentication token
        Token.objects.filter(user=request.user).delete()

        # Deactivate user sessions
        UserSession.objects.filter(
            user=request.user,
            session_key=request.session.session_key
        ).update(is_active=False)

        # Django logout
        logout(request)

        return Response({
            'success': True,
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': 'Logout failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_profile(request):
    """Get current user profile"""
    serializer = UserProfileSerializer(request.user)
    return Response({
        'success': True,
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_user_profile(request):
    """Update user profile"""
    serializer = UserProfileSerializer(
        request.user,
        data=request.data,
        partial=request.method == 'PATCH'
    )

    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        'success': False,
        'message': 'Profile update failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Change user password"""
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        # Delete all tokens to force re-login
        Token.objects.filter(user=user).delete()

        # Deactivate all sessions
        UserSession.objects.filter(user=user).update(is_active=False)

        return Response({
            'success': True,
            'message': 'Password changed successfully. Please login again.'
        }, status=status.HTTP_200_OK)

    return Response({
        'success': False,
        'message': 'Password change failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def request_password_reset(request):
    """Request password reset"""
    serializer = PasswordResetRequestSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = CustomUser.objects.get(email=email, is_active=True)

        # Create password reset token
        expires_at = timezone.now() + timedelta(hours=1)  # 1 hour expiry
        reset_token = PasswordResetToken.objects.create(
            user=user,
            expires_at=expires_at
        )

        # Send password reset email
        # send_password_reset_email(user, reset_token, request)

        return Response({
            'success': True,
            'message': 'Password reset email sent successfully'
        }, status=status.HTTP_200_OK)

    return Response({
        'success': False,
        'message': 'Password reset request failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def confirm_password_reset(request):
    """Confirm password reset with token"""
    serializer = PasswordResetConfirmSerializer(data=request.data)

    if serializer.is_valid():
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            reset_token = PasswordResetToken.objects.get(
                token=token,
                is_used=False
            )

            if reset_token.is_expired():
                return Response({
                    'success': False,
                    'message': 'Password reset token has expired'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Reset password
            user = reset_token.user
            user.set_password(new_password)
            user.save()

            # Mark token as used
            reset_token.is_used = True
            reset_token.save()

            # Delete all tokens and sessions
            Token.objects.filter(user=user).delete()
            UserSession.objects.filter(user=user).update(is_active=False)

            return Response({
                'success': True,
                'message': 'Password reset successful. Please login with your new password.'
            }, status=status.HTTP_200_OK)

        except PasswordResetToken.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid password reset token'
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'success': False,
        'message': 'Password reset confirmation failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_sessions(request):
    """Get user active sessions"""
    sessions = UserSession.objects.filter(user=request.user, is_active=True)
    serializer = UserSessionSerializer(sessions, many=True)

    return Response({
        'success': True,
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def terminate_session(request, session_key):
    """Terminate a specific session"""
    try:
        session = UserSession.objects.get(
            user=request.user,
            session_key=session_key,
            is_active=True
        )
        session.is_active = False
        session.save()

        # Delete Django session
        try:
            Session.objects.get(session_key=session_key).delete()
        except Session.DoesNotExist:
            pass

        return Response({
            'success': True,
            'message': 'Session terminated successfully'
        }, status=status.HTTP_200_OK)

    except UserSession.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def terminate_all_sessions(request):
    """Terminate all user sessions except current"""
    current_session = request.session.session_key

    # Deactivate all sessions except current
    UserSession.objects.filter(user=request.user, is_active=True).exclude(
        session_key=current_session
    ).update(is_active=False)

    # Delete all tokens except current (if using token auth)
    # Token.objects.filter(user=request.user).delete()

    return Response({
        'success': True,
        'message': 'All other sessions terminated successfully'
    }, status=status.HTTP_200_OK)
