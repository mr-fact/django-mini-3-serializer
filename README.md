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

# Model Serializer
The `ModelSerializer` class provides a shortcut that lets you automatically create a `Serializer` class with fields that correspond to the Model fields.

- it will automatically generate a set of fields for you, based on the model
- it will automatically generate validators for the serializer, such as unique_together validators.
- it includes simple default implementations of `.create()` and `.update()`.

``` python
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'account_name', 'users', 'created']
```

Any relationships such as foreign keys on the model will be mapped to `PrimaryKeyRelatedField`.

Reverse relationships are not included by default unless explicitly included as specified in the [serializer relations documentation](https://www.django-rest-framework.org/api-guide/relations/).

If you only want a subset of the default fields to be used in a model serializer, you can do so using `fields` or `exclude` options, just as you would with a `ModelForm`.It is strongly recommended that you explicitly set all fields that should be serialized using the `fields` attribute. This will make it less likely to result in unintentionally exposing data when your models change.

``` python
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'account_name', 'users', 'created']
        # OR
        # fields = '__all__'
        # OR
        # exclude = ['id', ]
```

## Specifying nested serialization
The `depth` option should be set to an integer value that indicates the depth of relationships that should be traversed before reverting to a flat representation.
``` python
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'account_name', 'users', 'created']
        depth = 1
```

## Specifying fields explicitly & read only fields
``` python
class AccountSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    groups = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = Account
        fields = ['url', 'groups']
        read_only_fields = ['account_name']
```
Model fields which have `editable=False` set, and `AutoField` fields will be set to read-only by default, and do not need to be added to the `read_only_fields` option.

**Note:** There is a special-case where a read-only field is part of a `unique_together` constraint at the model level. In this case the field is required by the serializer class in order to validate the constraint, but should also not be editable by the user.
``` python
user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
```
Please review the [Validators Documentation](https://www.django-rest-framework.org/api-guide/validators/) for details on the [UniqueTogetherValidator](https://www.django-rest-framework.org/api-guide/validators/#uniquetogethervalidator) and [CurrentUserDefault](https://www.django-rest-framework.org/api-guide/validators/#currentuserdefault) classes.

## Additional keywird arguments
`extra_kwargs = {}`
``` python
class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
```

## Relational fields
For full details see the [serializer relations documentation](https://www.django-rest-framework.org/api-guide/relations/).

## Customizing field mapping
`.serializer_field_mapping`
- A mapping of Django model fields to REST framework serializer fields. You can override this mapping to alter the default serializer fields that should be used for each model field.

`.serializer_related_field`
- This property should be the serializer field class, that is used for relational fields by default.
- For `ModelSerializer` this defaults to `serializers.PrimaryKeyRelatedField`.
- For `HyperlinkedModelSerializer` this defaults to `serializers.HyperlinkedRelatedField`.

`.serializer_url_field`
- The serializer field class that should be used for any `url` field on the serializer.
- Defaults to `serializers.HyperlinkedIdentityField`

`.serializer_choice_field`
- The serializer field class that should be used for any choice fields on the serializer.
- Defaults to `serializers.ChoiceField`


### The field_class and field_kwargs API
`.build_standard_field(self, field_name, model_field)`
- Called to generate a serializer field that maps to a standard model field.
- The default implementation returns a serializer class based on the `serializer_field_mapping` attribute.

`.build_relational_field(self, field_name, relation_info)`
- Called to generate a serializer field that maps to a relational model field.
- The default implementation returns a serializer class based on the serializer_related_field attribute.
- The relation_info argument is a named tuple, that contains model_field, related_model, to_many and has_through_model properties.

`.build_nested_field(self, field_name, relation_info, nested_depth)`
- Called to generate a serializer field that maps to a relational model field, when the depth option has been set.
- The default implementation dynamically creates a nested serializer class based on either ModelSerializer or HyperlinkedModelSerializer.
- The nested_depth will be the value of the depth option, minus one.
- The relation_info argument is a named tuple, that contains model_field, related_model, to_many and has_through_model properties.

`.build_property_field(self, field_name, model_class)`
- Called to generate a serializer field that maps to a property or zero-argument method on the model class.
- The default implementation returns a ReadOnlyField class.

`.build_url_field(self, field_name, model_class)`
- Called to generate a serializer field for the serializer's own url field. The default implementation returns a HyperlinkedIdentityField class.

`.build_unknown_field(self, field_name, model_class)`
- Called when the field name did not map to any model field or model property. The default implementation raises an error, although subclasses may customize this behavior.

## Hyperlinked Model Serializer
By default the serializer will include a `url` field instead of a `primary key field`.
``` python
class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = ['url', 'id', 'account_name', 'users', 'created']
```

### Absolute and relative URLs
When instantiating a `HyperlinkedModelSerializer` you must include the current `request` in the serializer context, for example:
``` python
serializer = AccountSerializer(queryset, context={'request': request})
# http://api.example.com/accounts/1/
```
If you do want to use relative URLs, you should explicitly pass `{'request': None} ` in the serializer context.
``` python
/accounts/1/
```

### How hyperlink views are determined
By default hyperlinks are expected to correspond to a view name that matches the style `'{model_name}-detail'`, and looks up the instance by a `pk` keyword argument.

You can override a URL field view name and lookup field by using either, or both of, the `view_name` and `lookup_field` options in the `extra_kwargs` setting, like so:
``` python
class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = ['account_url', 'account_name', 'users', 'created']
        extra_kwargs = {
            'url': {'view_name': 'accounts', 'lookup_field': 'account_name'},
            'users': {'lookup_field': 'username'}
        }
```
Alternatively you can set the fields on the serializer explicitly.
``` python
class AccountSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='accounts',
        lookup_field='slug'
    )
    users = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        lookup_field='username',
        many=True,
        read_only=True
    )

    class Meta:
        model = Account
        fields = ['url', 'account_name', 'users', 'created']
```
**Tip:** Properly matching together hyperlinked representations and your URL conf can sometimes be a bit fiddly. Printing the `repr` of a `HyperlinkedModelSerializer` instance is a particularly useful way to inspect exactly which view names and lookup fields the relationships are expected to map too.

### Changing the URL field name
The name of the URL field defaults to 'url'. You can override this globally, by using the `URL_FIELD_NAME` setting.


## List Serializer
When a serializer is instantiated and `many=True` is passed, a `ListSerializer` instance will be created.

**defaults:**
 - `allow_empty=True`
 - `max_length=None`
 - `min_length=None`

### Custom ListSerializer
``` python
class CustomListSerializer(serializers.ListSerializer):
    ...

class CustomSerializer(serializers.Serializer):
    ...
    class Meta:
        list_serializer_class = CustomListSerializer
```
for multiple object creation is to simply call `.create()` for each item in the list.
``` python
class BookListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        books = [Book(**item) for item in validated_data]
        return Book.objects.bulk_create(books)

class BookSerializer(serializers.Serializer):
    ...
    class Meta:
        list_serializer_class = BookListSerializer
```
By default the `ListSerializer` class does not support `multiple updates`.
When writing your `.update()` make sure to keep the following in mind:
 - How do you determine which instance should be updated for each item in the list of data?
 - How should insertions be handled? Are they invalid, or do they create new objects?
 - How should removals be handled? Do they imply object deletion, or removing a relationship? Should they be silently ignored, or are they invalid?
 - How should ordering be handled? Does changing the position of two items imply any state change or is it ignored?
``` python
class BookListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        # Maps for id->instance and id->data item.
        book_mapping = {book.id: book for book in instance}
        data_mapping = {item['id']: item for item in validated_data}

        # Perform creations and updates.
        ret = []
        for book_id, data in data_mapping.items():
            book = book_mapping.get(book_id, None)
            if book is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(book, data))

        # Perform deletions.
        for book_id, book in book_mapping.items():
            if book_id not in data_mapping:
                book.delete()

        return ret

class BookSerializer(serializers.Serializer):
    # We need to identify elements in the list using their primary key,
    # so use a writable field here, rather than the default which would be read-only.
    id = serializers.IntegerField()
    ...

    class Meta:
        list_serializer_class = BookListSerializer
```
`many=True` -> `.__init__()` in `Serializer` and also `ListSerializer`

Occasionally you might need to explicitly specify how the child and parent classes should be instantiated when `many=True` is passed. You can do so by using the `many_init` class method.
``` python
    @classmethod
    def many_init(cls, *args, **kwargs):
        # Instantiate the child serializer.
        kwargs['child'] = cls()
        # Instantiate the parent list serializer.
        return CustomListSerializer(*args, **kwargs)
```

## Base Serializer
 - `.data` returns the outgoing primitive representation
 - `.is_valid()` deserializes and validates incoming data
 - `.validatied_data` returns the validated incoming data
 - `.errors` returns any errors during validation
 - `.save()` persists the validated data into an object instance

 - `.to_representaion()` override this to support serialization for read operations
 - `.to_internal_value()` override this to support deserialization for write operations
 - `.create()` and `.update()` override either or both of these to support saving instances

 `BaseSerializer` provides the same interface as the `Serializer` or `ModelSerializer`.

The only difference you'll notice when doing so is the `BaseSerializer` classes will not **generate HTML forms** in the browsable API.

### Read-Only BaseSerializer classes
we just need to override the `.to_representation()` method.
``` python
class HighScore(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    player_name = models.CharField(max_length=10)
    score = models.IntegerField()

class HighScoreSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'score': instance.score,
            'player_name': instance.player_name
        }

# single HighScode instances
@api_view(['GET'])
def high_score(request, pk):
    instance = HighScore.objects.get(pk=pk)
    serializer = HighScoreSerializer(instance)
    return Response(serializer.data)

# multiple HighScode instances
@api_view(['GET'])
def all_high_scores(request):
    queryset = HighScore.objects.order_by('-score')
    serializer = HighScoreSerializer(queryset, many=True)
    return Response(serializer.data)
```

### Read-Write serializer classes
`.to_internal_value()` method returns the validated values that will be used to construct the object instance, and may raise a `serializers.ValidationError` if the supplied data is in an incorrect format.

`.to_internal_value()` -> `.is_valid()` + `.validated_data` + `.errors`

`.save()` -> `.create()` + `.update()`
``` python
class HighScoreSerializer(serializers.BaseSerializer):
    def to_internal_value(self, data):
        score = data.get('score')
        player_name = data.get('player_name')

        # Perform the data validation.
        if not score:
            raise serializers.ValidationError({
                'score': 'This field is required.'
            })
        if not player_name:
            raise serializers.ValidationError({
                'player_name': 'This field is required.'
            })
        if len(player_name) > 10:
            raise serializers.ValidationError({
                'player_name': 'May not be more than 10 characters.'
            })

        # Return the validated values. This will be available as
        # the `.validated_data` property.
        return {
            'score': int(score),
            'player_name': player_name
        }

    def to_representation(self, instance):
        return {
            'score': instance.score,
            'player_name': instance.player_name
        }

    def create(self, validated_data):
        return HighScore.objects.create(**validated_data)
```

## Advanced Serializer usage
### overriding serialization and deserialization behavior
If you need to alter the serialization or deserialization behavior of a serializer class, you can do so by overriding the `.to_representation()` or `.to_internal_value()` methods.

**why:**
- Adding new behavior for new serializer base classes.
- Modifying the behavior slightly for an existing class.
- Improving serialization performance for a frequently accessed API endpoint that returns lots of data.

**instance** -> `to_representation()` -> **data**
``` python
def to_representation(self, instance):
    """Convert `username` to lowercase."""
    ret = super().to_representation(instance)
    ret['username'] = ret['username'].lower()
    return ret
```

**initial_data** -> `.to_internal_value()` -> **validated_data**

If you don't need to alter deserialization behavior and instead want to provide object-level validation, it's recommended that you instead override the `.validate()` method.

### Serializer inheritance
``` python
class MyBaseSerializer(Serializer):
    my_field = serializers.CharField()

    def validate_my_field(self, value):
        ...

class MySerializer(MyBaseSerializer):
    ...
```
If you want the `Meta class` to inherit from a parent class you must do so explicitly. For example:
``` python
class AccountSerializer(MyBaseSerializer):
    class Meta(MyBaseSerializer.Meta):
        model = Account
```
It’s possible to declaratively remove a `Field` inherited from a parent class.
``` python
class MyBaseSerializer(ModelSerializer):
    my_field = serializers.CharField()

class MySerializer(MyBaseSerializer):
    my_field = None
```

### Dynamically modifying fields
Modifying the `fields` argument directly allows you to do interesting things such as changing the arguments on serializer fields at `runtime`, rather than at the point of declaring the serializer.
``` python
class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
```
``` python
>>> class UserSerializer(DynamicFieldsModelSerializer):
>>>     class Meta:
>>>         model = User
>>>         fields = ['id', 'username', 'email']
>>>
>>> print(UserSerializer(user))
{'id': 2, 'username': 'jonwatts', 'email': 'jon@example.com'}
>>>
>>> print(UserSerializer(user, fields=('id', 'email')))
{'id': 2, 'email': 'jon@example.com'}
```

### Customizing the default fields
REST framework 2 provided an API to allow developers to override how a `ModelSerializer` class would automatically generate the default set of fields.

This API included the `.get_field()`, `.get_pk_field()` and other methods.

Because the serializers have been fundamentally redesigned with 3.0 this API no longer exists. You can still modify the fields that get created but you'll need to refer to the source code, and be aware that if the changes you make are against private bits of API then they may be subject to change.

## Third party packages

### django Rest marshmallow
The [django-rest-marshmallow](https://marshmallow-code.github.io/django-rest-marshmallow/) package provides an alternative implementation for serializers, using the python [marshmallow](https://marshmallow.readthedocs.io/en/latest/) library.

## serpy
The [serpy](https://github.com/clarkduvall/serpy) package is an alternative implementation for serializers that is built for **speed**. Serpy serializes complex datatypes to simple native types. The **native types** can be easily converted to JSON or any other format needed.

## MongoengineModelSerializer
The [django-rest-framework-mongoengine](https://github.com/umutbozkurt/django-rest-framework-mongoengine) package provides a `MongoEngineModelSerializer` serializer class that supports using **MongoDB** as the storage layer for Django REST framework.

## GeoFeatureModelSerializer
The [django-rest-framework-gis](https://github.com/djangonauts/django-rest-framework-gis) package provides a `GeoFeatureModelSerializer` serializer class that supports **GeoJSON** both for read and write operations.

## HStoreSerializer
The [django-rest-framework-hstore](https://github.com/djangonauts/django-rest-framework-hstore) package provides an `HStoreSerializer` to support [django-hstore](https://github.com/djangonauts/django-hstore) `DictionaryField` model field and its `schema-mode` feature.

## Dynamic REST
The [dynamic-rest](https://github.com/AltSchool/dynamic-rest) package extends the ModelSerializer and ModelViewSet interfaces, adding API query parameters for filtering, sorting, and including / excluding all fields and relationships defined by your serializers.

## Dynamic Fields Mixin
The [drf-dynamic-fields](https://github.com/dbrgn/drf-dynamic-fields) package provides a mixin to dynamically limit the fields per serializer to a subset specified by an URL parameter.

## DRF FlexFields
The [drf-flex-fields](https://github.com/rsinger86/drf-flex-fields) package extends the ModelSerializer and ModelViewSet to provide commonly used functionality for dynamically setting fields and expanding primitive fields to nested models, both from URL parameters and your serializer class definitions.

## Serializer Extensions
The [django-rest-framework-serializer-extensions](https://github.com/evenicoulddoit/django-rest-framework-serializer-extensions) package provides a collection of tools to DRY up your serializers, by allowing fields to be defined on a per-view/request basis. Fields can be whitelisted, blacklisted and child serializers can be optionally expanded.

## HTML JSON Forms
The [html-json-forms](https://github.com/wq/html-json-forms) package provides an algorithm and serializer for processing `<form>` submissions per the (inactive) [HTML JSON Form specification](https://www.w3.org/TR/html-json-forms/). The serializer facilitates processing of arbitrarily nested JSON structures within HTML. For example, `<input name="items[0][id]" value="5">` will be interpreted as `{"items": [{"id": "5"}]}`.

## DRF-Base64
[DRF-Base64](https://bitbucket.org/levit_scs/drf_base64) provides a set of field and model serializers that handles the upload of base64-encoded files.

## QueryFields
[djangorestframework-queryfields](https://djangorestframework-queryfields.readthedocs.io/) allows API clients to specify which fields will be sent in the response via inclusion/exclusion query parameters.

## DRF Writable Nested
The [drf-writable-nested](https://github.com/beda-software/drf-writable-nested) package provides writable nested model serializer which allows to create/update models with nested related data.

## DRF Encrypt Content
The [drf-encrypt-content](https://github.com/oguzhancelikarslan/drf-encrypt-content) package helps you encrypt your data, serialized through ModelSerializer. It also contains some helper functions. Which helps you to encrypt your data.
