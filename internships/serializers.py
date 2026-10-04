from rest_framework import serializers
from .models import Internship


class InternshipSerializer(serializers.ModelSerializer):

    company = serializers.StringRelatedField()


    class Meta:

        model = Internship

        fields = [
            "id",
            "title",
            "description",
            "company",
            "location",
            "internship_type",
            "duration",
            "deadline",
            "created_at",
            "active",
        ]