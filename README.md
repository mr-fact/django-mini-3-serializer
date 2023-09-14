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
