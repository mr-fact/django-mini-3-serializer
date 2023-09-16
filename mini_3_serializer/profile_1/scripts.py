from profile_1.models import MyUser
from profile_1.serializers import UserSerializer


# instance -> data(JSON)
def serializing():
    instance = MyUser.objects.get_or_create_user('test1', 'test1')
    serializer = UserSerializer(instance=instance)
    print('serializing: instance -> data(JSON)')
    print()
    print('instance:', instance)
    print('instance.username:', instance.username)
    print('instance.password:', instance.password)
    print('instance.my_profile.first_name:', instance.my_profile.first_name)
    print('instance.my_profile.last_name:', instance.my_profile.last_name)
    print('instance.my_profile.birthdate:', instance.my_profile.birthdate)
    print()
    print('serializer.instance:', serializer.instance)
    print('serializer.instance.username:', serializer.instance.username)
    print('serializer.instance.password:', serializer.instance.password)
    print('serializer.data:', serializer.data)


# data(JSON) -> validation -> instance
def deserializing():
    data = {
        'username': 'invalid_user',
        # 'password': 'invalid_user',
    }
    serializer = UserSerializer(data=data)
    print('deserializing: data(JSON) -> instance')
    print()
    print('data: ', data)
    print()
    print('serializer.is_valid():', serializer.is_valid())
    print('serializer.errors:', serializer.errors)
    print()
    print('serializer.instance:', serializer.instance)
    print('serializer.data:', serializer.data)
    print('serializer.validated_data:', serializer.validated_data)


# data(JSON) -> validation -> instance
def deserializing_valid():
    data = {
        'username': 'invalid_user',
        'password': 'invalid_user',
        'profile': {
            'first_name': 'test2 first name',
            'last_name': 'test2 last name',
            'birthdate': '2023-09-16',
        }
    }
    serializer = UserSerializer(data=data)
    print('deserializing: data(JSON) -> instance')
    print()
    print('data: ', data)
    print()
    print('serializer.is_valid():', serializer.is_valid())
    print('serializer.errors:', serializer.errors)
    print()
    print('serializer.instance:', serializer.instance)
    print('serializer.data:', serializer.data)
    print('serializer.validated_data:', serializer.validated_data)


def run(func):
    """
        functions:
        - serializing
        - deserializing
        - deserializing_valid
    """
    print('\n\n\n')
    title = f'run: {func.__name__}'
    print('#'*(len(title)+4))
    print(f'# {title} #')
    print('#'*(len(title)+4))
    func()


run(serializing)
run(deserializing)
run(deserializing_valid)
