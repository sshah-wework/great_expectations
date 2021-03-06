# PYTHON 2 - py2 - update to ABC direct use rather than __metaclass__ once we drop py2 support
from abc import ABCMeta, abstractmethod

from six import string_types


class StoreBackend(object):
    __metaclass__ = ABCMeta
    """A store backend acts as a key-value store that can accept tuples as keys, to abstract away
    reading and writing to a persistence layer.

    In general a StoreBackend implementation must provide implementations of:
      - _get
      - _set
      - list_keys
      - _has_key
    """

    def __init__(self, fixed_length_key=False):
        self._fixed_length_key = fixed_length_key

    @property
    def fixed_length_key(self):
        return self._fixed_length_key

    def get(self, key):
        self._validate_key(key)
        value = self._get(key)
        return value

    def set(self, key, value, **kwargs):
        self._validate_key(key)
        self._validate_value(value)
        # Allow the implementing setter to return something (e.g. a path used for its key)
        return self._set(key, value, **kwargs)

    def has_key(self, key):
        self._validate_key(key)
        return self._has_key(key)

    def get_url_for_key(self, key, protocol=None):
        raise NotImplementedError(
            "Store backend of type {0:s} does not have an implementation of get_url_for_key".format(
                type(self).__name__))

    def _validate_key(self, key):
        if isinstance(key, tuple):
            for key_element in key:
                if not isinstance(key_element, string_types):
                    raise TypeError(
                        "Elements within tuples passed as keys to {0} must be instances of {1}, not {2}".format(
                            self.__class__.__name__,
                            string_types,
                            type(key_element),
                        ))
        else:
            raise TypeError("Keys in {0} must be instances of {1}, not {2}".format(
                self.__class__.__name__,
                tuple,
                type(key),
            ))

    def _validate_value(self, value):
        pass

    @abstractmethod
    def _get(self, key):
        raise NotImplementedError

    @abstractmethod
    def _set(self, key, value, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def list_keys(self, prefix=()):
        raise NotImplementedError

    def _has_key(self, key):
        raise NotImplementedError


class InMemoryStoreBackend(StoreBackend):
    """Uses an in-memory dictionary as a store backend.
    """

    # noinspection PyUnusedLocal
    def __init__(self, runtime_environment=None, fixed_length_key=False):
        super(InMemoryStoreBackend, self).__init__(fixed_length_key=fixed_length_key)
        self._store = {}

    def _get(self, key):
        return self._store[key]

    def _set(self, key, value, **kwargs):
        self._store[key] = value

    def list_keys(self, prefix=()):
        return [key for key in self._store.keys() if key[:len(prefix)] == prefix]

    def _has_key(self, key):
        return key in self._store
