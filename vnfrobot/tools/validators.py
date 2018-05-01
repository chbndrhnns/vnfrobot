from __future__ import absolute_import

import re
from abc import ABCMeta, abstractmethod

import validators
from robot.libraries.BuiltIn import BuiltIn

import exc


class Validator:
    __metaclass__ = ABCMeta

    def __init__(self, context=None):
        self.context = context
        self.name = self.__class__.__name__

    @abstractmethod
    def validate(self, entity):
        pass


class Service(Validator):
    def __init__(self, context):
        super(Service, self).__init__(context)
        if not self.context:
            raise exc.ValidationError('Context is necessary for the validator "{}"'.format(self.name))

    def validate(self, entity):
        return entity in self.context


class Url(Validator):
    def __init__(self):
        Validator.__init__(self)

    def validate(self, val):
        return validators.url(val)


class Port(Validator):
    def __init__(self):
        Validator.__init__(self)

    def validate(self, val):
        try:
            val = int(val)
            return validators.between(val, 1, 65535)
        except ValueError:
            return False


class Domain(Validator):
    def __init__(self):
        Validator.__init__(self)

    def validate(self, val):
        try:
            return validators.domain(val)
        except Exception:
            pass


class IpAddress(Validator):
    def __init__(self):
        Validator.__init__(self)

    def validate(self, val):
        # hack: :: is a valid IPv6 address
        if val == '::':
            return True
        try:
            return validators.ipv4(val) or (validators.ipv6(val))
        except Exception:
            pass


class Context(Validator):
    def __init__(self, context):
        super(Context, self).__init__(context)
        if not self.context:
            raise exc.ValidationError('Context is necessary for the validator "{}"'.format(self.name))

    def validate(self, entity=None):
        if entity not in self.context:
            BuiltIn().log('Context "{}" not allowed. Must be any of {}'.format(entity, self.context), level='ERROR',
                          console=True)
            return False
        return True


class Property(Validator):
    def __init__(self, context):
        super(Property, self).__init__(context)
        if not self.context:
            raise exc.ValidationError('Context is necessary for the validator "{}"'.format(self.name))
        if not isinstance(self.context, dict):
            raise exc.ValidationError('Context must be of instance dict()'.format())

    def validate(self, entity):
        if entity not in self.context.keys():
            BuiltIn().log('Property "{}" not allowed. Must be any of {}'.format(entity, self.context), level='ERROR',
                          console=True)
            return False
        return True


class InList(Validator):
    def __init__(self, context):
        super(InList, self).__init__(context)
        if not self.context:
            raise exc.ValidationError('Context is necessary for the validator "{}"'.format(self.name))
        if not isinstance(self.context, list):
            raise exc.ValidationError('Context must be of instance list()'.format())

    def validate(self, entity):
        return entity in self.context


class Regex(Validator):
    def __init__(self, context):
        super(Regex, self).__init__(context)
        if not self.context:
            raise exc.ValidationError('Context is necessary for the validator "{}"'.format(self.name))
        if not isinstance(self.context, basestring):
            raise exc.ValidationError('Context must be of instance basestring()'.format())
        else:
            try:
                re.compile(self.context)
            except re.error:
                raise exc.ValidationError('Context must be a valid regex'.format())

    def validate(self, entity):
        found = re.search(self.context, entity)
        if not found:
            BuiltIn().log('Value "{}" not allowed. Must match the regex {}'.format(entity, self.context), level='ERROR',
                          console=True)
            return False
        return True