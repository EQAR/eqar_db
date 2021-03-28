
class ReadWriteSerializerMixin(object):
    """
    Overrides get_serializer_class to choose:

    - the list serializer for GET requests on the collection,
    - the read serializer for GET requests on objects,
    - the write serializer for POST requests.

    Adapted from https://www.revsys.com/tidbits/using-different-read-and-write-serializers-django-rest-framework/
    """

    list_serializer_class = None
    read_serializer_class = None
    write_serializer_class = None

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return self.get_write_serializer_class()
        elif self.action == "list":
            return self.get_list_serializer_class()
        else:
            return self.get_read_serializer_class()

    def get_read_serializer_class(self):
        assert self.read_serializer_class is not None, (
            f"'{self.__class__.__name__}' should either include a `read_serializer_class` attribute, or override the `get_read_serializer_class()` method."
        )
        return self.read_serializer_class

    def get_list_serializer_class(self):
        assert self.list_serializer_class is not None or self.read_serializer_class is not None, (
            f"'{self.__class__.__name__}' should either include a `list_serializer_class` or `read_serializer_class` attribute, or override the `get_list_serializer_class()` method."
        )
        if self.list_serializer_class is not None:
            return self.list_serializer_class
        else:
            return self.read_serializer_class

    def get_write_serializer_class(self):
        assert self.write_serializer_class is not None, (
            f"'{self.__class__.__name__}' should either include a `write_serializer_class` attribute, or override the `get_write_serializer_class()` method."
        )
        return self.write_serializer_class

