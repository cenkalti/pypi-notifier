from pypi_notifier import db


class ModelMixin(object):

    @classmethod
    def get_or_create(cls, **kwargs):
        instance = db.session.query(cls).filter_by(**kwargs).first()
        if not instance:
            instance = cls(**kwargs)
        return instance
