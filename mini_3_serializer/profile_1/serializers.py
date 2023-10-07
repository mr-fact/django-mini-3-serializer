from rest_framework import serializers
from rest_framework.fields import empty

from profile_1.models import MyUser, MyProfile, MyImage


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyProfile
        fields = [
            'first_name',
            'last_name',
            'birthdate',
        ]


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyImage
        fields = [
            'image',
        ]


class UserSerializer(serializers.ModelSerializer):
    # images = ImageSerializer(required=False, many=True)
    my_profile = ProfileSerializer(required=False)

    class Meta:
        model = MyUser
        fields = [
            'username',
            'password',
            # 'images',
            'my_profile',
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def is_valid(self, *, raise_exception=False):
        print('\t+[deserializing->is_valid()]')
        result = super().is_valid()
        print('\t-[\t->is_valid()]')
        return result

    def run_validation(self, data=empty):
        print('\t+[deserializing->run_validation()]')
        result = super().run_validation(data)
        print('\t-[\t->run_validation()]')
        return result

    def validate_empty_values(self, data):
        print('\t+[deserializing->validate_empty_values()]')
        result = super().validate_empty_values(data)
        print('\t-[\t->validate_empty_values()]')
        return result

    def to_internal_value(self, data):
        print('\t+[deserializing->to_internal_value()]')
        result = super().to_internal_value(data)
        print('\t-[\t->to_internal_value()]')
        return result

    def run_validators(self, value):
        print('\t+[deserializing->run_validators()]')
        result = super().run_validators(value)
        print('\t-[\t->run_validators()]')
        return result

    def validate_username(self, data):
        print('\t+[deserializing->field_validate()]')
        result = data
        print('\t-[\t->field_validate()]')
        return result

    def validate(self, attrs):
        print('\t+[deserializing->validate()]')
        result = attrs
        print('\t-[\t->validate()]')
        return result

    def to_representation(self, instance):
        print('\t+[serializing->to_representation()]')
        super_data = super().to_representation(instance)
        super_data['new_field'] = 'new_field_value'
        result = super_data
        print('\t-[\t->to_representation()]')
        return result

    def create(self, validated_data):
        instance = MyUser.objects.create_user(
            username=validated_data.get('username'),
            password=validated_data.get('password'),
            first_name=validated_data.get('my_profile').get('first_name'),
            last_name=validated_data.get('my_profile').get('last_name'),
            birthdate=validated_data.get('my_profile').get('birthdate'),
        )
        return instance

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        new_password = validated_data.get('password', None)
        if new_password:
            instance.set_password(new_password)

        profile_data = validated_data.pop('my_profile', None)
        if profile_data:
            instance.my_profile.first_name = profile_data.get('first_name', instance.my_profile.first_name)
            instance.my_profile.last_name = profile_data.get('last_name', instance.my_profile.last_name)
            instance.my_profile.birthdate = profile_data.get('birthdate', instance.my_profile.birthdate)
        instance.save()
        return instance

    # def save(self, **kwargs):
    #     pass


class UserHyperLinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'username', 'url', ]
