from django.contrib.auth import get_user_model
from rest_framework import serializers, viewsets

from ClubManager.permissions import AutoListPermissionViewSetMixin
from .models import Member


class FamilyMemberField(serializers.RelatedField):
    def to_representation(self, value) -> str | None:
        return f"{value.user.first_name} {value.user.last_name} <{value.user.email}>"

    def to_internal_value(self, data) -> Member:
        email = data.split("<")[1].split(">")[0]
        return get_user_model().objects.get(email=email).member


class MemberSerializer(serializers.ModelSerializer):
    family_members = FamilyMemberField(many=True, queryset=Member.objects.all())
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.CharField(source="user.email")

    class Meta:
        model = Member
        fields = ["id", "first_name", "last_name", "email", "birthday", "license", "phone_number", "emergency_phone_number", "family_members"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        family_members = validated_data.pop("family_members")

        user = get_user_model().objects.get_or_create(**user_data, username=user_data["email"])[0]
        member = Member.objects.get_or_create(user=user)[0]

        for attr, value in validated_data.items():
            setattr(member, attr, value)

        family_members = [m for m in family_members if m.id != member.id]
        member.family_members.set(family_members)
        member.save()

        return member

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user")
        family_members = validated_data.pop("family_members")

        super().update(instance, validated_data)

        for attr, value in user_data.items():
            setattr(instance.user, attr, value)

        instance.user.save()

        family_members = [m for m in family_members if m.id != instance.id]
        instance.family_members.set(family_members)

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["family_members"] = [member for member in data["family_members"] if member != f"{instance.user.first_name} {instance.user.last_name} <{instance.user.email}>"]

        return data


class MembersViewSet(AutoListPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
