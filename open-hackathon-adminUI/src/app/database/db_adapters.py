class DBAdapter(object):
    def __init__(self, db):
        self.db = db


class SQLAlchemyAdapter(DBAdapter):

    def __init__(self, db):
        super(SQLAlchemyAdapter, self).__init__(db)

    def get_object(self, ObjectClass, id):
        """ Retrieve one object specified by the primary key 'pk' """
        return ObjectClass.query.get(id)

    def find_all_objects(self, ObjectClass, **kwargs):
        """ Retrieve all objects matching the case sensitive filters in 'kwargs'. """

        # Convert each name/value pair in 'kwargs' into a filter
        query = ObjectClass.query
        for field_name, field_value in kwargs.items():

            # Make sure that ObjectClass has a 'field_name' property
            field = getattr(ObjectClass, field_name, None)
            if field is None:
                raise KeyError(
                    "SQLAlchemyAdapter.find_first_object(): Class '%s' has no field '%s'." % (ObjectClass, field_name))

            # Add a filter to the query
            # _in do not support relationship query now, use foreign key instead
            # _in do not support None
            query = query.filter(field.in_((field_value,)))

        # Execute query
        return query.all()

    def find_all_objects_like(self, ObjectClass, **kwargs):
        """ Retrieve all objects matching the case sensitive filters in 'kwargs'. """

        # Convert each name/value pair in 'kwargs' into a filter
        query = ObjectClass.query
        for field_name, field_value in kwargs.items():

            # Make sure that ObjectClass has a 'field_name' property
            field = getattr(ObjectClass, field_name, None)
            if field is None:
                raise KeyError(
                    "SQLAlchemyAdapter.find_first_object(): Class '%s' has no field '%s'." % (ObjectClass, field_name))

            # Add a filter to the query
            query = query.filter(field.like((field_value,)))

        # Execute query
        return query.all()

    def count(self, ObjectClass, **kwargs):
        """ Retrieve all objects matching the case sensitive filters in 'kwargs'. """

        # Convert each name/value pair in 'kwargs' into a filter
        query = ObjectClass.query
        for field_name, field_value in kwargs.items():

            # Make sure that ObjectClass has a 'field_name' property
            field = getattr(ObjectClass, field_name, None)
            if field is None:
                raise KeyError(
                    "SQLAlchemyAdapter.find_first_object(): Class '%s' has no field '%s'." % (ObjectClass, field_name))

            # Add a filter to the query
            query = query.filter(field.in_((field_value,)))

        # Execute query
        return query.count()

    def filter(self, ObjectClass, *criterion):
        query = ObjectClass.query
        return query.filter(*criterion)
    
    def filter_by(self, ObjectClass, **kwargs):
        query = ObjectClass.query
        return query.filter_by(**kwargs)

    def find_first_object(self, ObjectClass, **kwargs):
        """ Retrieve the first object matching the case sensitive filters in 'kwargs'. """

        # Convert each name/value pair in 'kwargs' into a filter
        query = ObjectClass.query
        for field_name, field_value in kwargs.items():

            # Make sure that ObjectClass has a 'field_name' property
            field = getattr(ObjectClass, field_name, None)
            if field is None:
                raise KeyError(
                    "SQLAlchemyAdapter.find_first_object(): Class '%s' has no field '%s'." % (ObjectClass, field_name))

            # Add a case sensitive filter to the query
            query = query.filter(field == field_value)  # case sensitive!!

        # Execute query
        return query.first()

    def ifind_first_object(self, ObjectClass, **kwargs):
        """ Retrieve the first object matching the case insensitive filters in 'kwargs'. """

        # Convert each name/value pair in 'kwargs' into a filter
        query = ObjectClass.query
        for field_name, field_value in kwargs.items():

            # Make sure that ObjectClass has a 'field_name' property
            field = getattr(ObjectClass, field_name, None)
            if field is None:
                raise KeyError(
                    "SQLAlchemyAdapter.find_first_object(): Class '%s' has no field '%s'." % (ObjectClass, field_name))

            # Add a case sensitive filter to the query
            query = query.filter(field.ilike(field_value))  # case INsensitive!!

        # Execute query
        return query.first()

    def add_object(self, inst):
        self.db.session.add(inst)

    def add_object_kwargs(self, ObjectClass, **kwargs):
        """ Add an object of class 'ObjectClass' with fields and values specified in '**kwargs'. """
        object = ObjectClass(**kwargs)
        self.db.session.add(object)
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
        self.db.session.delete(object)

    def delete_all_objects(self, ObjectClass, **kwargs):
        """ Delete all objects matching the case sensitive filters in 'kwargs'. """

        # Convert each name/value pair in 'kwargs' into a filter
        query = ObjectClass.query
        for field_name, field_value in kwargs.items():

            # Make sure that ObjectClass has a 'field_name' property
            field = getattr(ObjectClass, field_name, None)
            if field is None:
                raise KeyError(
                    "SQLAlchemyAdapter.find_first_object(): Class '%s' has no field '%s'." % (ObjectClass, field_name))

            # Add a filter to the query
            query = query.filter(field.in_((field_value,)))

        # Execute delete
        # query filter by in_ do not support none args, use synchronize_session=False instead
        query.delete(synchronize_session=False)

    def commit(self):
        self.db.session.commit()