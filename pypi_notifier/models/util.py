import json

from sqlalchemy.types import TypeDecorator, Text

from pypi_notifier import db, sentry


class JSONType(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""

    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


def skip_errors(objects):
    for obj in objects:
        try:
            yield obj
        except Exception:
            sentry.captureException()
            db.session.rollback()
