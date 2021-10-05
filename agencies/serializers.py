from rest_framework import serializers

from uni_db.serializers import ListSerializer, DetailSerializer


class ApplicationSerializer(DetailSerializer):

    def validate(self, data):
        """
        Some sanity checks
        """
        if data['stage'] == '8. Completed' and not data['result']:
            raise serializers.ValidationError("Decisions needs to be specified for completed decisions.")
        return data

