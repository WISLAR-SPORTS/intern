from rest_framework import serializers
from .models import Student


class StudentSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username"
    )


    class Meta:

        model = Student

        fields = [
            "username",
            "course",
            "skills",
            "cv"
        ]