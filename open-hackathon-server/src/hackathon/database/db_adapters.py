# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------


class SQLAlchemyAdapterMetaClass(type):
    @staticmethod
    def wrap(func):
        """Return a wrapped instance method"""

        def auto_commit(self, *args, **kwargs):
            try:
                # todo a trick for DB transaction issue
                self.commit()
                return_value = func(self, *args, **kwargs)
                self.commit()
                return return_value
            except:
                self.rollback()
                raise

        return auto_commit

    def __new__(mcs, name, bases, attrs):
        """If the method in this list, DON'T wrap it"""
        no_wrap = ["commit", "merge", "rollback", "remove", "session"]

        def wrap(method):
            """private methods are not wrapped"""
            if method not in no_wrap and not method.startswith("__"):
                attrs[method] = mcs.wrap(attrs[method])

        map(lambda m: wrap(m), attrs.keys())
        return super(SQLAlchemyAdapterMetaClass, mcs).__new__(mcs, name, bases, attrs)


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

    def session(self):
        return self.db_session

    # ------------------------------ methods that no need to wrap --- end------------------------------

    # ------------------------------ auto wrapped 'public' methods  --- start ------------------------------
    def get_object(self, object_class, primary_id):
        """ Retrieve one object specified by the primary key 'pk' """
        return object_class.query.get(primary_id)

    def find_all_objects(self, object_class, *criterion):
        return object_class.query.filter(*criterion).all()

    def find_all_objects_by(self, object_class, **kwargs):
        return object_class.query.filter_by(**kwargs).all()

    def find_all_objects_order_by(self, object_class, limit=None, *order_by, **kwargs):
        if limit is not None:
            return object_class.query.filter_by(**kwargs).order_by(*order_by).limit(limit)
        else:
            return object_class.query.filter_by(**kwargs).order_by(*order_by).all()

    def count(self, object_class, *criterion):
        return object_class.query.filter(*criterion).count()

    def count_by(self, object_class, **kwargs):
        return object_class.query.filter_by(**kwargs).count()

    def find_first_object(self, object_class, *criterion):
        return object_class.query.filter(*criterion).first()

    def find_first_object_by(self, object_class, **kwargs):
        return object_class.query.filter_by(**kwargs).first()

    def add_object(self, inst):
        self.db_session.add(inst)

    def add_object_kwargs(self, object_class, **kwargs):
        """ Add an object of class 'object_class' with fields and values specified in '**kwargs'. """
        instance = object_class(**kwargs)
        self.db_session.add(instance)
        return instance

    def update_object(self, instance, **kwargs):
        """ Update object 'object' with the fields and values specified in '**kwargs'. """
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
            else:
                raise KeyError("Object '%s' has no field '%s'." % (type(instance), key))

    def delete_object(self, instance):
        """ Delete object 'object'. """
        self.db_session.delete(instance)

    def delete_all_objects(self, object_class, *criterion):
        return object_class.query.filter(*criterion).delete(synchronize_session=False)

    def delete_all_objects_by(self, object_class, **kwargs):
        """ Delete all objects matching the case sensitive filters in 'kwargs'. """

        # Convert each name/value pair in 'kwargs' into a filter
        query = object_class.query.filter_by(**kwargs)

        # query filter by in_ do not support none args, use synchronize_session=False instead
        return query.delete(synchronize_session=False)

    def paginate(self, query, page, per_page=20, error_out=False):
        """Returns `per_page` items from page `page`.

        :param query: BaseQuery object of the DB model

        :type page: int
        :param page: the page number. start from 1

        :type per_page: int
        :param per_page: items of each page

        :type error_out: bool
        :param error_out: throw Exception or not when no items found

        :rtype: Pagination
        :return an :class:`Pagination` object. See https://pythonhosted.org/Flask-SQLAlchemy/api.html#flask.ext.sqlalchemy.Pagination for more
        """
        return query.paginate(page, per_page, error_out)

# ------------------------------ auto wrapped 'public' methods  --- end ------------------------------
