from django.core.exceptions import ObjectDoesNotExist


def get_attribute(obj: object, *args, default=None):
    """
    Returns attribute of an object if the object and attribute
    exists. If either of them do not exist then it returns the default.
    Can pass in more attributes to chain.
    i.e. get_attribute(obj, attr1, attr2) which equals obj.attr1.attr2
    Need to catch ObjectDoesNotExist because if try  get_attribute(a,b,c)
    and 'b' is None then that exception is raised, therefore catches it and
    returns the default.
    """
    if obj:
        for arg in args:
            try:
                attr = getattr(obj, arg, default)
                obj = attr
            except ObjectDoesNotExist:
                return default
        return obj if obj is not None else default
    return default
