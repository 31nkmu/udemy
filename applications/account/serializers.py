from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_enumfield import EnumField
import enum

from applications.account import tasks

User = get_user_model()


class Experience(enum.Enum):
    self = 'self',
    professional = 'professional'
    online = 'online'
    other = 'other'


class Audience(enum.Enum):
    no = 'no'
    small = 'small'
    medium = 'medium'


class Types(enum.Enum):
    user = 'u'
    mentor = 'm'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, required=True)
    password_confirm = serializers.CharField(min_length=6, required=True, write_only=True)
    type = EnumField(choices=Types, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'type', 'password_confirm')

    def validate(self, attrs):
        p1 = attrs['password']
        p2 = attrs['password_confirm']
        if p1 != p2:
            raise serializers.ValidationError({'msg': 'пароли не совпадают'})
        return attrs

    def create(self, validated_data):
        is_mentor = validated_data['type'].value == 'm'
        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password'],
            type=validated_data['type'],
            is_mentor=is_mentor
        )
        code = user.activation_code
        tasks.send_user_activation_link.delay(validated_data['email'], code)
        return user


class MentorSerializer(serializers.ModelSerializer):
    experience = EnumField(choices=Experience, required=True)
    audience = EnumField(choices=Audience, required=True)

    class Meta:
        model = User
        fields = ('experience', 'audience')

    def create(self, validated_data):
        user = self.context.get('request').user
        if not user.is_mentor:
            raise serializers.ValidationError({'msg': 'только ментор может заполнить эти поля'})
        user.experience = validated_data['experience']
        user.audience = validated_data['audience']
        user.save(update_fields=['experience', 'audience'])
        return user


class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    @staticmethod
    def validate_email(email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('нет такого зарегистрированного пользователя')
        return email

    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        user.create_activation_code()
        user.save(update_fields=['activation_code'])
        tasks.send_change_password_code.delay(email=user.email, confirm_code=user.activation_code)
        return user


class ChangePasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True, min_length=6)
    password_confirm = serializers.CharField(required=True, write_only=True, min_length=6)

    def validate(self, attrs):
        p1 = attrs['password']
        p2 = attrs['password_confirm']
        if p1 != p2:
            raise serializers.ValidationError({'msg': 'Пароли не совпадают'})
        return attrs

    @staticmethod
    def validate_code(code):
        if not User.objects.filter(activation_code=code).exists():
            raise serializers.ValidationError({'msg': 'неправельный код подтверждения'})
        return code

    @staticmethod
    def validate_email(email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'msg': 'пользователь с данным именем не найден'})
        return email

    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.activation_code = ''
        user.save(update_fields=['password', 'activation_code'])
        return user
