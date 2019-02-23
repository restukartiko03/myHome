from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import generics, mixins, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Door, DoorLog, ElectricityAccount, Lamp, Token
from core.serializers import (
    DoorLogSerializer,
    DoorSerializer,
    ElectricityAccountSerializer,
    LampSerializer,
    LoginSerializer,
    TokenSerializer,
    UserSerializer,
)


class DoorLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = DoorLog.objects.all()
    serializer_class = DoorLogSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = User.objects.filter(username=request.data['username']).first()
        if user is None:
            return Response('User With Username ' + request.data['username'] + ' Not Found')
            
        door = Door.objects.filter(house_id=request.data['id'], owner=user).first()
        if door is None:
            return Response({'success': False})
        log = DoorLog.objects.create(door=door)
        
        return Response({'success': True})


class DoorViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Door.objects.all()
    serializer_class = DoorSerializer
    # permission_classes = (permissions.IsAuthenticated,)

    @action(methods=['post'], detail=False)
    def lock_unlock(self, request):
        user = User.objects.filter(username=request.data['username']).first()
        if user is None:
            return Response({'success': False})
        
        door = Door.objects.filter(owner__username=user.username, house_id=request.data['id']).first()
        if door is None:
            return Response({'success': False})
        else:
            door.locked = not(door.locked)
            door.save()

        return Response({'success': True})


class ElectricityAccountViewSet(viewsets.ModelViewSet):
    queryset = ElectricityAccount.objects.all()
    serializer_class = ElectricityAccountSerializer
    permission_classes = (permissions.IsAuthenticated,)


class LampViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Lamp.objects.all()
    serializer_class = LampSerializer
    # permission_classes = (permissions.IsAuthenticated,)

    @action(methods=['post'], detail=False)
    def turn_on_off(self, request):
        user = User.objects.filter(username=request.data['username']).first()
        if user is None:
            return Response({'success': False})
        
        lamp = Lamp.objects.filter(owner__username=user.username, house_id=request.data['id']).first()
        if lamp is None:
            return Response({'success': False})
        else:
            lamp.on = not(lamp.on)
            lamp.save()

        return Response({'success': True})


class TokenViewSet(viewsets.ModelViewSet):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer

    @transaction.atomic
    @action(methods=['post'], detail=False)
    def use_token(self, request):
        account = ElectricityAccount.objects.filter(account_number=request.data['account_number']).first()
        token = Token.objects.filter(code=request.data['code']).first()
        
        if account is None or token is None:
            return Response({'success': False})
        else:
            account.balance += token.balance
            token.used = True
            account.save()
            token.save()

        return Response({'success': True})

class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = User.objects.create_user(username=request.data['username'], email=request.data['email'], password=request.data['password'])
        door = Door.objects.create(owner=user, house_id=1)

        for i in range(3):
            lamp = Lamp.objects.create(owner=user, house_id=i+1)

        return Response(UserSerializer(user).data)


class LoginViewSet(viewsets.GenericViewSet):
    serializer_class = LoginSerializer

    def create(self, request, *arg, **kwargs):
        user = authenticate(username=request.data['username'], password=request.data['password'])
        
        if not user:
            return Response({'success': False})
        else:
            return Response({'success': True})
