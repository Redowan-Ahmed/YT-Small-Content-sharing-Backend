from rest_framework import serializers
from .models import UserProfile
from djoser.serializers import UserCreateSerializer


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'get_full_name', 'email', 'first_name', 'last_name']


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'password']



class UserCreatePasswordRetypeSerializer(UserCreateSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["re_password"] = serializers.CharField(
            style={"input_type": "password"}
        )

    def validate(self, attrs):
        self.fields.pop("re_password", None)
        re_password = attrs.pop("re_password")
        attrs = super().validate(attrs)
        if attrs["password"] == re_password:
            return attrs
        else:
            raise serializers.ValidationError({'re_password':"Re_Password Does not match with password"})
