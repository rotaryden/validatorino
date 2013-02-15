# Validatorino is released under the LGPL
#
# Copyright 2013, Denis Volokhovski
#

class ValidationError(Exception):
    def __init__(self, dic):
        self.message = "\n\nVALIDATION error: fields/errors: \n\n" + repr(dic)
    
    def message(self):
        return self.message
    
    def __str__(self):
        return self.message


class _VALIDATORS(object):
    @classmethod
    def len(cls, *args):
        return ''


class Validator(object):
    _SEPARATOR = '*'
    _ARGLIST_SEP = ":"
    _ARG_SEP = ","

    def __init__(self, custom_validators):
        self.get_validator = \
            lambda func_name: getattr(custom_validators, func_name, getattr(_VALIDATORS, func_name)) \
            if custom_validators \
            else lambda func_name: getattr(_VALIDATORS, func_name)

    def _validator_reduce_gen(self, name):
        def validator(val, func_name_with_args):
            parts = func_name_with_args.split(self._ARGLIST_SEP)
            func = self.get_validator(parts[0] or name)  # name in case of omitting validators like 'email*'
            return func(val, () if len(parts) < 2 else parts[1].split(self._ARG_SEP))
        return validator

    def validate(self, fields_dict):
        """
            Usage: {'field_name*first_validator*second_validator': value, ...},
            ---> validates like second_validator(first_validator(value))
            ommited validator: 'email*' --> 'email*email',  ''email*upper**len:5,4' --> 'email*upper*email*len(5)
        """
        result = {}
        errors = {}
        for field_name, field_value in fields_dict.iteritems():
            parts = field_name.split(self._SEPARATOR)
            if len(parts) > 1:
                name = parts[0]
                # noinspection PyTypeChecker
                err_description = reduce(
                    self._validator_reduce_gen(name), parts[1:], field_value)
                if err_description:
                    errors[name] = err_description
                    # no sense here to assign result[]
                else:
                    result[name] = field_value
            else:
                result[field_name] = field_value
        if errors:
            raise ValidationError(errors)
        # return original dictionary with stripped validator specs
        return result