

class ObjectView(object):
    """
    Wrap a dictionary so its properties can be accessed as an object.

    Parameters
    ----------
    d : dictionary
        The dictionary to wrap.
    """
    def __init__(self, d):
        self.__dict__ = d

    def __str__(self):
        """
        Override string representation to output wrapped dictionary.
        """
        return str(self.__dict__)
