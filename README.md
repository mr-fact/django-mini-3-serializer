# django-mini-3-serializer

منبع : https://www.django-rest-framework.org/api-guide/serializers/

سریالایزر در کل رابط بین دو سمت کاربر و دیتابیسه

json <--------> instance of model

## Declaring Serializers
هیچی 

## Serializing Objects
instance -> data(JSON)
``` python
serializer = CommentSerializer(comment)
serializer.data
# {'email': 'leila@example.com', 'content': 'foo bar', 'created': '2016-01-27T15:17:10.375877'}
```

## Deserializing Objects
data(JSON) -> instance
``` python
serializer = CommentSerializer(data=data)
serializer.is_valid()
# True
serializer.validated_data
# {'content': 'foo bar', 'email': 'leila@example.com', 'created': datetime.datetime(2012, 08, 22, 16, 20, 09, 822243)}
```
## Saving instances

`.create()` -> for create new instance

`.update()` -> for update available instances

``` python
class CommentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    content = serializers.CharField(max_length=200)
    created = serializers.DateTimeField()

    def create(self, validated_data):
        return Comment(**validated_data)

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.content = validated_data.get('content', instance.content)
        instance.created = validated_data.get('created', instance.created)
        instance.save()
        return instance
```

`.save()` -> will either create a new instance, or update an existing instance, depending on if an existing instance was passed when instantiating the serializer class:
``` python
# .save() will create a new instance.
serializer = CommentSerializer(data=data)

# .save() will update the existing `comment` instance.
serializer = CommentSerializer(comment, data=data)
```

**Passing additional attributes to `.save()`:**
``` python
serializer.save(owner=request.user)
```

**Overriding `.save()` directly:**
``` python
class ContactForm(serializers.Serializer):
    email = serializers.EmailField()
    message = serializers.CharField()

    def save(self):
        email = self.validated_data['email']
        message = self.validated_data['message']
        send_email(from=email, message=message)
```


## Validation
When deserializing data, you always need to cal `.is_valid()` before attempting to access the `.validated_data`, or `.save()` an object instance.

there are also validation errors in the `.errors`

`{'non_field_errors':''}` -> general validation errors
``` python
serializer = CommentSerializer(data={'email': 'foobar', 'content': 'baz'})
serializer.is_valid()
# False
serializer.errors
# {'email': ['Enter a valid e-mail address.'], 'created': ['This field is required.']}
```

### Raising an exception on invalid data
`.is_Valid()` ->  catch `serializers.ValidationError` -> responce `HTTP 400 BAD REQUEST`

``` python
# Return a 400 response if the data was invalid.
serializer.is_valid(raise_exception=True)
```

### field-level validation
`.validate_<field_name>()`
``` python
from rest_framework import serializers

class BlogPostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    content = serializers.CharField()

    def validate_title(self, value):
        """
        Check that the blog post is about Django.
        """
        if 'django' not in value.lower():
            raise serializers.ValidationError("Blog post is not about Django")
        return value
```

`(required=False)` -> this validation step will not take place if the field is not included.

### object-level validation
`.validate()`
``` python
from rest_framework import serializers

class EventSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=100)
    start = serializers.DateTimeField()
    finish = serializers.DateTimeField()

    def validate(self, data):
        """
        Check that start is before finish.
        """
        if data['start'] > data['finish']:
            raise serializers.ValidationError("finish must occur after start")
        return data
```

### validators
function based validator
``` python
def multiple_of_ten(value):
    if value % 10 != 0:
        raise serializers.ValidationError('Not a multiple of ten')

class GameRecord(serializers.Serializer):
    score = IntegerField(validators=[multiple_of_ten])
```
class based validator
``` python
class EventSerializer(serializers.Serializer):
    name = serializers.CharField()
    room_number = serializers.IntegerField(choices=[101, 102, 103, 201])
    date = serializers.DateField()

    class Meta:
        # Each room only has one event per day.
        validators = [
            UniqueTogetherValidator(
                queryset=Event.objects.all(),
                fields=['room_number', 'date']
            )
        ]
```


## Accessing the initial data and instance
When passing an initial object or queryset to a serializer instance, the object will be made available as `.instance`. If no initial object is passed then the `.instance` attribute will be `None`.
``` python
EventSerializer(instance=event).instance
# event

EventSerializer().instance
# None
```
When passing data to a serializer instance, the unmodified data will be made available as `.initial_data`. If the `data` keyword argument is not passed then the `.initial_data` attribute will `not exist`.
``` python
EventSerializer(data=event).initial_data
# initial_data

EventSerializer().initial_data
# error
```

## Partial updates
``` python
# Update `comment`
serializer = CommentSerializer(comment, data={'content': 'foo bar', 'email': 'mr-fact202020@gmail.com'})

# Update `comment` with partial data
serializer = CommentSerializer(comment, data={'content': 'foo bar'}, partial=True)
```

## Dealing with nested objects
The **Serializer** class is itself a type of **Field**
``` python
class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=100)
```
``` python
class CommentSerializer(serializers.Serializer):
    user = UserSerializer()
    content = serializers.CharField(max_length=200)
    created = serializers.DateTimeField()

class CommentSerializer(serializers.Serializer):
    user = UserSerializer(required=False)  # May be an anonymous user.
    ...

class CommentSerializer(serializers.Serializer):
    edits = EditItemSerializer(many=True)  # A nested list of 'edit' items.
    ...
```

### Writable nested representaions
``` python
serializer = CommentSerializer(data={'user': {'email': 'foobar', 'username': 'doe'}, 'content': 'baz'})
serializer.is_valid()
# False
serializer.errors
# {'user': {'email': ['Enter a valid e-mail address.']}, 'created': ['This field is required.']}
```
Similarly, the `.validated_data` property will include nested data structures.

### Writing `.create()` or `.update()` methods for nested representaitons
For updates you'll want to think carefully about how to handle `.update()` to relationships. For example if the data for the relationship is `None`, or not provided, which of the following should occur?
 - Set the relationship to **NULL** in the database.
 - **Delete** the associated instance.
 - **Ignore** the data and leave the instance as it is.
 - Raise a validation **error**.

``` python
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'email', 'profile']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        Profile.objects.create(user=user, **profile_data)
        return user

     def update(self, instance, validated_data):
            profile_data = validated_data.pop('profile')
            # Unless the application properly enforces that this field is
            # always set, the following could raise a `DoesNotExist`, which
            # would need to be handled.
            profile = instance.profile
    
            instance.username = validated_data.get('username', instance.username)
            instance.email = validated_data.get('email', instance.email)
            instance.save()
    
            profile.is_premium_member = profile_data.get(
                'is_premium_member',
                profile.is_premium_member
            )
            profile.has_support_contract = profile_data.get(
                'has_support_contract',
                profile.has_support_contract
             )
            profile.save()
    
            return instance
```
The default `ModelSerializer` `.create()` and `.update()` methods do not include support for **writable nested representations**.

third-party packages that support automatic writable nested representaions -> [**DRF Writable Nested**](https://github.com/beda-software/drf-writable-nested)

### write custom model manager classes that handle creating the correct instances.
``` python
class UserManager(models.Manager):
    ...

    def create(self, username, email, is_premium_member=False, has_support_contract=False):
        user = User(username=username, email=email)
        user.save()
        profile = Profile(
            user=user,
            is_premium_member=is_premium_member,
            has_support_contract=has_support_contract
        )
        profile.save()
        return user
```
Our `.create()` method on the serializer class can now be re-written to use the new manager method.
``` python
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    def create(self, validated_data):
        return User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            is_premium_member=validated_data['profile']['is_premium_member'],
            has_support_contract=validated_data['profile']['has_support_contract']
        )
```
Django documentation on [**model managers**](https://docs.djangoproject.com/en/stable/topics/db/managers/)

## Dealing with multiple objects
### serializing multiple objects
``` python
queryset = Book.objects.all()
serializer = BookSerializer(queryset, many=True)
serializer.data
# [
#     {'id': 0, 'title': 'The electric kool-aid acid test', 'author': 'Tom Wolfe'},
#     {'id': 1, 'title': 'If this is a man', 'author': 'Primo Levi'},
#     {'id': 2, 'title': 'The wind-up bird chronicle', 'author': 'Haruki Murakami'}
# ]
```
### deserializing multiple objects
The default behavior for deserializing multiple objects is to **support multiple object creation**, but **not support multiple object updates**.
For more information on how to support or customize either of these cases, see the [ListSerializer](https://www.django-rest-framework.org/api-guide/serializers/#listserializer) documentation below.

## including extra context
``` python
serializer = AccountSerializer(account, context={'request': request})
serializer.data
# {'id': 6, 'owner': 'denvercoder9', 'created': datetime.datetime(2013, 2, 12, 09, 44, 56, 678870), 'details': 'http://example.com/accounts/6/details'}
```
The context dictionary can be used within any serializer field logic, such as a custom `.to_representation()` method, by accessing the `self.context` attribute.
