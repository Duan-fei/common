# -*- coding:utf-8 -*-


def key_sort(data):
    """
    sort by dict key and return sorted list

    :param data:  dict to sort
    :type data: dict
    :return: sorted list of k,v tuple
    :rtype: list
    """
    return [(k, data[k]) for k in sorted(data.keys())]


def recursive_sort(data):
    """
    Recursive sort dict
    :param data: data to sort
    :type data: dict
    :return: sorted list
    :rtype: list
    """
    result = []
    for k, v in key_sort(data):
        if v is dict:
            v = key_sort(v)
        result.append((k, v))
    return result


try:
    text = (str, unicode)
except NameError:
    text = str


def hashable_identity(obj):
    if hasattr(obj, '__func__'):
        return id(obj.__func__), id(obj.__self__)
    elif hasattr(obj, 'im_func'):
        return id(obj.im_func), id(obj.im_self)
    elif isinstance(obj, text):
        return obj
    else:
        return id(obj)


# cast method
def cast(child_class, parental_obj):
    child_obj = child_class()
    for attr_name in parental_obj.__dict__:
        setattr(child_obj, attr_name, getattr(parental_obj, attr_name))
    return child_obj