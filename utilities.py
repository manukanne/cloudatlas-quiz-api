def first_or_default(iterable):
    """
    Gets the first or default (= None) value from an iterable
    :param iterable: Iterable instance
    :return: First item or None
    """
    return next(iter(iterable or []), None)
