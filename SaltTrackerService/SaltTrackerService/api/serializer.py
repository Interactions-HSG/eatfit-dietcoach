
from rest_framework import serializers
from api.models import AvatarData
from api.models import SaltTrackerUser, Category, FoodItem, FoodRecord, ProfileData, StudyDay, Study, CustomText, FoodItemSupplement, FoodRecordSupplement
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'

class FoodItemSupplementSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodItemSupplement
        fields = '__all__'

class FoodItemSerializer(serializers.ModelSerializer):
    supplements = serializers.SerializerMethodField(read_only=True)

    def get_supplements(self, obj):
        show_all_supplements = self.context.get("show_all_supplements")
        if not show_all_supplements:
            s = FoodItemSupplementSerializer(obj.supplements.filter(show_in_foodtracker = True), many=True)
        else:
            s = FoodItemSupplementSerializer(obj.supplements.all(), many=True)
        return s.data

    class Meta:
        model = FoodItem
        fields = '__all__'

class FoodRecordSerializer(serializers.ModelSerializer):
    icon = serializers.CharField(source="food_item.icon", required=False, allow_null=True)
    food_item_name = serializers.CharField(source="food_item.name", required=False, allow_null=True)
    supplement_names = serializers.SerializerMethodField(read_only=True)

    def get_supplement_names(self, obj):
        return FoodRecordSupplement.objects.filter(food_record = obj).values_list("food_item_supplement__name", flat=True)

    class Meta:
        model = FoodRecord
        fields = '__all__'

class FoodRecordSupplementSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodRecordSupplement
        fields = ("id",)

class FoodRecordCreateSerializer(serializers.ModelSerializer):
    icon = serializers.CharField(source="food_item.icon", required=False, allow_null=True)
    food_item_name = serializers.CharField(source="food_item.name", required=False, allow_null=True)
    date = serializers.DateTimeField()
    supplements = serializers.ListField(child = serializers.DictField(), required = False, allow_null=True)

    class Meta:
        model = FoodRecord
        exclude = ("study_day",)

class FoodRecordCreateSaltSerializer(serializers.ModelSerializer):
    icon = serializers.CharField(source="food_item.icon", required=False, allow_null=True)
    food_item_name = serializers.CharField(source="food_item.name", required=False, allow_null=True)
    date = serializers.DateTimeField()
    supplements = serializers.DictField(child = serializers.FloatField(), required = False, allow_null=True)

    class Meta:
        model = FoodRecord
        exclude = ("study_day",)

class ProfileDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileData
        fields = '__all__'

class CustomTextSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomText
        fields = '__all__'


class StudyDaySerializer(serializers.ModelSerializer):

    class Meta:
        model = StudyDay
        fields = '__all__'

class StudySerializer(serializers.ModelSerializer):

    class Meta:
        model = Study
        fields = '__all__'

class SaltTrackerUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    username = serializers.CharField(source="user.username")
    last_name = serializers.CharField(source="user.last_name")
    first_name = serializers.CharField(source="user.first_name")
    password = serializers.CharField(source="user.password", required=False)
    id = serializers.IntegerField(source="user.id")
    food_tracker_user = serializers.BooleanField(required = False)

    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('remove_fields', None)
        super(SaltTrackerUserSerializer, self).__init__(*args, **kwargs)

        if remove_fields:
            # for multiple fields in a list
            for field_name in remove_fields:
                self.fields.pop(field_name)

    class Meta:
        model = SaltTrackerUser
        fields = ('id', 'date_of_birth', 'height', 'email', 'first_name', 'last_name', 'password','username',
                  'weight','country','zip','sex', "nickname", 'notification_id', 'operating_system', 'cumulus_password', 'cumulus_email', "food_tracker_user")

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data["user"]["username"], password=validated_data["user"]["password"],email=validated_data["user"]["email"], first_name=validated_data["user"]["first_name"], last_name=validated_data["user"]["last_name"])
        salt_tracker_user = SaltTrackerUser.objects.create(user=user,date_of_birth=validated_data["date_of_birth"],weight = validated_data["weight"], height = validated_data["height"],
                                                  sex=validated_data["sex"], nickname=validated_data["nickname"], cumulus_email=validated_data.get('cumulus_email', None),cumulus_password=validated_data.get('cumulus_password', None), food_tracker_user = validated_data.get("food_tracker_user", False))  
        return salt_tracker_user


    def update(self, instance, validated_data):
        user_dict = validated_data.get("user", None)
        if user_dict:
            instance.user.password = user_dict.get('password', instance.user.password)
            instance.user.first_name = user_dict.get('first_name', instance.user.first_name)
            instance.user.last_name = user_dict.get('last_name', instance.user.last_name)
            instance.user.email = user_dict.get('email', instance.user.email)
            instance.user.save()
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.zip = validated_data.get('zip', instance.zip)
        instance.country = validated_data.get('country', instance.country)
        instance.sex = validated_data.get('sex', instance.sex)
        instance.notification_id = validated_data.get('notification_id', instance.notification_id)
        instance.operating_system = validated_data.get('operating_system', instance.operating_system)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.height = validated_data.get('height', instance.height)
        instance.cumulus_email = validated_data.get('cumulus_email', instance.cumulus_email)
        instance.cumulus_password = validated_data.get('cumulus_password', instance.cumulus_password)
        instance.save() 
        return instance

class DateLockedSerializer(serializers.Serializer):
    date = serializers.DateTimeField()
    is_locked = serializers.BooleanField()

class InitalUserDataSerializer(serializers.Serializer):
    user_data = SaltTrackerUserSerializer(remove_fields=['password'])
    study_data = StudySerializer()
    first_week = DateLockedSerializer(many=True)
    total_days = serializers.IntegerField()
    total_open_days = serializers.IntegerField()
    average_salt = serializers.FloatField(required=False)

class AvatarDataSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AvatarData
        exclude = ('user',)
