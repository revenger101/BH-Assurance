from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser, UserSession
import re


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'email', 'name', 'phone_number', 'user_type', 
            'password', 'password_confirm'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'name': {'required': True},
            'user_type': {'required': True},
        }
    
    def validate_email(self, value):
        """Validate email format and uniqueness"""
        if CustomUser.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def validate_name(self, value):
        """Validate name format"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")

        # Check if name contains only letters, numbers, spaces, and common punctuation
        if not re.match(r'^[a-zA-Z0-9\s\.\-\']+$', value):
            raise serializers.ValidationError("Name can only contain letters, numbers, spaces, dots, hyphens, and apostrophes.")

        return value.strip().title()
    
    def validate_phone_number(self, value):
        """Validate phone number if provided"""
        if value and CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value
    
    def validate_user_type(self, value):
        """Validate user type"""
        valid_types = ['CLIENT', 'USER']
        if value not in valid_types:
            raise serializers.ValidationError(f"User type must be one of: {', '.join(valid_types)}")
        return value
    
    def validate(self, attrs):
        """Validate password confirmation and strength"""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Password confirmation does not match.'
            })
        
        # Validate password strength
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})
        
        return attrs
    
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate login credentials"""
        email = attrs.get('email', '').lower()
        password = attrs.get('password', '')
        
        if not email or not password:
            raise serializers.ValidationError('Email and password are required.')
        
        # Authenticate user
        user = authenticate(email=email, password=password)
        
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')
        
        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'name', 'phone_number', 'user_type',
            'is_verified', 'date_joined', 'profile_picture', 'bio'
        ]
        read_only_fields = ['id', 'email', 'user_type', 'is_verified', 'date_joined']
    
    def validate_name(self, value):
        """Validate name format"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")

        if not re.match(r'^[a-zA-Z0-9\s\.\-\']+$', value):
            raise serializers.ValidationError("Name can only contain letters, numbers, spaces, dots, hyphens, and apostrophes.")

        return value.strip().title()
    
    def validate_phone_number(self, value):
        """Validate phone number uniqueness"""
        if value and CustomUser.objects.filter(phone_number=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    
    current_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate_current_password(self, value):
        """Validate current password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value
    
    def validate(self, attrs):
        """Validate new password confirmation"""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'New password confirmation does not match.'
            })
        
        # Validate password strength
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError({'new_password': e.messages})
        
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate email exists"""
        if not CustomUser.objects.filter(email=value.lower(), is_active=True).exists():
            raise serializers.ValidationError('No active user found with this email address.')
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    
    token = serializers.UUIDField(required=True)
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate password reset token and new password"""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'Password confirmation does not match.'
            })
        
        # Validate password strength
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError({'new_password': e.messages})
        
        return attrs


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for user sessions"""
    
    class Meta:
        model = UserSession
        fields = [
            'session_key', 'ip_address', 'user_agent', 
            'created_at', 'last_activity', 'is_active'
        ]
        read_only_fields = ['session_key', 'created_at']
