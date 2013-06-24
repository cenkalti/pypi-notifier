import json
from sqlalchemy.types import TypeDecorator, UnicodeText


class JSONType(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""

    impl = UnicodeText

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value
