import json
import logging
import traceback
from contextlib import contextmanager

from sqlalchemy.types import TypeDecorator, Text

from pypi_notifier.extensions import db


logger = logging.getLogger(__name__)


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


@contextmanager
def commit_or_rollback():
    try:
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.error(''.join(traceback.format_exc()))
