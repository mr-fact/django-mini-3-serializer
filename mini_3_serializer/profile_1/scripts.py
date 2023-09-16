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
        'passwordd': 'invalid_user',
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
        'my_profile': {
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


def create_user():
    # delete exist user
    try:
        instance = MyUser.objects.get(username='test3')
        instance.delete()
    except MyUser.DoesNotExist:
        pass

    # create new user
    data = {
        'username': 'test3',
        'password': 'test3',
        'my_profile': {
            'first_name': 'test3 first name',
            'birthdate': '2023-09-16',
        }
    }
    serializer = UserSerializer(data=data)
    print('deserializing: data(JSON) -> instance -> save(create)')
    print()
    print('data: ', data)
    print()
    print('serializer.is_valid():', serializer.is_valid())
    print('serializer.errors:', serializer.errors)
    if serializer.is_valid():
        print('serializer.save():', serializer.save())
    print()
    print('serializer.instance:', serializer.instance)
    print('serializer.data:', serializer.data)
    print('serializer.validated_data:', serializer.validated_data)


def update_user():
    print('deserializing: data(JSON) ans instance -> instance -> save(update)')

    # delete exist user
    try:
        instance = MyUser.objects.get(username='test4')
        instance.delete()
    except MyUser.DoesNotExist:
        pass

    create_user()
    instance = MyUser.objects.get(username='test3')
    new_data = {
        'username': 'test4',
        'my_profile': {
            'last_name': 'test4 last name',
        }
    }

    # update data
    serializer = UserSerializer(instance=instance, data=new_data)
    print('serializer.is_valid():', serializer.is_valid())
    print('serializer.errors:', serializer.errors)
    if serializer.is_valid():
        print('serializer.save():', serializer.save())
    print()
    print('serializer.instance.username:', serializer.instance.username)
    print('serializer.instance.first_name:', serializer.instance.my_profile.first_name)
    print('serializer.instance.last_name:', serializer.instance.my_profile.last_name)
    print('serializer.data:', serializer.data)


def run(func):
    """
        functions:
        - serializing
        - deserializing
        - deserializing_valid
        - update_user
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
run(create_user)
run(update_user)
