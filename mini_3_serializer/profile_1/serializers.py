from rest_framework import serializers

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
