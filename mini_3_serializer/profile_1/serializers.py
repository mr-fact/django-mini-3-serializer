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
    profile = ProfileSerializer(required=False, source='my_profile')

    class Meta:
        model = MyUser
        fields = [
            'username',
            'password',
            # 'images',
            'profile',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def save(self, **kwargs):
        pass
