from rest_framework import serializers
from rest_framework.fields import empty

from profile_1.logs import start_end_log, message_log, level_log
from profile_1.models import MyUser, MyProfile, MyImage


class ProfileSerializer(serializers.ModelSerializer):
    @start_end_log
    @message_log('PS')
    @level_log(1)
    def bind(self, field_name, parent):
        return super().bind(field_name, parent)

    @start_end_log
    @message_log('PS')
    @level_log(1)
    def to_representation(self, instance):
        return super().to_representation(instance)

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
    # custom_field = CustomField()

    class Meta:
        model = MyUser
        fields = [
            'username',
            'password',
            # 'images',
            'my_profile',
            # 'custom_field',
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    @start_end_log
    def is_valid(self, *, raise_exception=False):
        result = super().is_valid()
        return result

    @start_end_log
    def run_validation(self, data=empty):
        result = super().run_validation(data)
        return result

    @start_end_log
    def validate_empty_values(self, data):
        result = super().validate_empty_values(data)
        return result

    @start_end_log
    def to_internal_value(self, data):
        result = super().to_internal_value(data)
        return result

    @start_end_log
    def run_validators(self, value):
        result = super().run_validators(value)
        return result

    @start_end_log
    def validate_username(self, data):
        result = data
        return result

    @start_end_log
    def validate(self, attrs):
        result = attrs
        return result

    @start_end_log
    @message_log('US')
    def to_representation(self, instance):
        super_data = super().to_representation(instance)
        super_data['new_field'] = 'new_field_value'
        result = super_data
        return result

    @start_end_log
    def get_custom_char_field(self):
        return 'aa'

    @start_end_log
    def save(self, **kwargs):
        result = super().save(**kwargs)
        return result

    @start_end_log
    def create(self, validated_data):
        instance = MyUser.objects.create_user(
            username=validated_data.get('username'),
            password=validated_data.get('password'),
            first_name=validated_data.get('my_profile').get('first_name'),
            last_name=validated_data.get('my_profile').get('last_name'),
            birthdate=validated_data.get('my_profile').get('birthdate'),
        )
        result = instance
        return result

    @start_end_log
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
        result = instance
        return result


class UserHyperLinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'username', 'url', ]
