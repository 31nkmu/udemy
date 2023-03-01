from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response

from applications.account.serializers import RegisterSerializer, MentorSerializer, ChangePasswordSerializer, \
    ChangePasswordConfirmSerializer

User = get_user_model()


class RegisterAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class ActivationAPIVIew(ListAPIView):
    def get(self, request, activation_code):
        try:
            user = User.objects.get(activation_code=activation_code)
            user.is_active = True
            user.activation_code = ''
            user.save(update_fields=['is_active', 'activation_code'])
            return Response({'msg': 'ваш аккаунт успешно активирован'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'msg': 'неверный код активации'})


class MentorAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = MentorSerializer


class ChangePasswordAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer


class ChangePasswordConfirmAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangePasswordConfirmSerializer
