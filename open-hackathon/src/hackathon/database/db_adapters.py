class SQLAlchemyAdapterMetaClass(type):
    @staticmethod
    def wrap(func):
        """Return a wrapped instance method"""

        def auto_commit(self, *args, **kwargs):
            try:
                return_value = func(self, *args, **kwargs)
                self.commit()
                return return_value
            except:
                self.rollback()
                raise

        return auto_commit

    def __new__(cls, name, bases, attrs):
        """If the method in this list, DON'T wrap it"""
        no_wrap = ["commit", "merge", "rollback", "remove"]

        def wrap(method):
            """private methods are not wrapped"""
            if method not in no_wrap and not method.startswith("__"):
                attrs[method] = cls.wrap(attrs[method])

        map(lambda m: wrap(m), attrs.keys())
        return super(SQLAlchemyAdapterMetaClass, cls).__new__(cls, name, bases, attrs)


class DBAdapter(object):
    def __init__(self, db_session):
        self.db_session = db_session


class SQLAlchemyAdapter(DBAdapter):
    """Use MetaClass to make this class"""
    __metaclass__ = SQLAlchemyAdapterMetaClass

    def __init__(self, db_session):
        super(SQLAlchemyAdapter, self).__init__(db_session)


    # ------------------------------ methods that no need to wrap --- start ------------------------------

    def commit(self):
        self.db_session.commit()

    def remove(self):
        self.db_session.remove()

    def merge(self, obj):
        self.db_session.merge(obj)

    def rollback(self):
        self.db_session.rollback()

    # ------------------------------ methods that no need to wrap --- end------------------------------

    # ------------------------------ auto wrapped 'public' methods  --- start ------------------------------
    def get_object(self, ObjectClass, id):
        """ Retrieve one object specified by the primary key 'pk' """
        return ObjectClass.query.get(id)

    def find_all_objects(self, ObjectClass, *criterion):
        return ObjectClass.query.filter(*criterion).all()

    def find_all_objects_by(self, ObjectClass, **kwargs):
        return ObjectClass.query.filter_by(**kwargs).all()

    def count(self, ObjectClass, *criterion):
        return ObjectClass.query.filter(*criterion).count()

    def count_by(self, ObjectClass, **kwargs):
        return ObjectClass.query.filter_by(**kwargs).count()

    def find_first_object(self, ObjectClass, *criterion):
        return ObjectClass.query.filter(*criterion).first()

    def find_first_object_by(self, ObjectClass, **kwargs):
        return ObjectClass.query.filter_by(**kwargs).first()

    def add_object(self, inst):
        self.db_session.add(inst)

    def add_object_kwargs(self, ObjectClass, **kwargs):
        """ Add an object of class 'ObjectClass' with fields and values specified in '**kwargs'. """
        object = ObjectClass(**kwargs)
        self.db_session.add(object)
        return object

    def update_object(self, object, **kwargs):
        """ Update object 'object' with the fields and values specified in '**kwargs'. """
        for key, value in kwargs.items():
            if hasattr(object, key):
                setattr(object, key, value)
            else:
                raise KeyError("Object '%s' has no field '%s'." % (type(object), key))

    def delete_object(self, object):
        """ Delete object 'object'. """
        self.db_session.delete(object)

    def delete_all_objects(self, ObjectClass, *criterion):
        ObjectClass.query.filter(*criterion).delete(synchronize_session=False)

    def delete_all_objects_by(self, ObjectClass, **kwargs):
        """ Delete all objects matching the case sensitive filters in 'kwargs'. """

        # Convert each name/value pair in 'kwargs' into a filter
        query = ObjectClass.query.filter_by(**kwargs)

        # query filter by in_ do not support none args, use synchronize_session=False instead
        query.delete(synchronize_session=False)

        # ------------------------------ auto wrapped 'public' methods  --- end ------------------------------