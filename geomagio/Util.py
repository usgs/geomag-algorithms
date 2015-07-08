class ObjectView(object):
    def __init__(self, d):
        self.__dict__ = d

    def __str__(self):
        return str(self.__dict__)
