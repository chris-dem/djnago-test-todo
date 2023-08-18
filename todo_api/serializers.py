from rest_framework import serializers

from .models import Todo


class TodoSerializer(serializers.ModelSerializer):
    """
    Serializer class of the tood model
    """

    class Meta:
        model = Todo
        fields = [
            "id",
            "title",
            "description",
            "timestamp_creation",
            "timestamp_updated",
            "status",
        ]

    def to_representation(self, instance):
        """
        to_representation
        Determines the representaion of the data
        of the deserializer

        Parameters
        ----------
        instance : Todo
            Todo instance

        Returns
        -------
        dict
            dictionary style of the intended representation form
        """
        data = super().to_representation(instance)
        # Convert status to human readable form
        data["status"] = instance.get_status_display()
        return data
