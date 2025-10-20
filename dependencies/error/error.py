class Result:
    def __init__(self, value=None, error=None):
        if value is None and error is None:
            raise ValueError("Both can't be None")

        self.__value = value
        self.__error = error

    def __bool__(self):
        return self.__value is not None

    @property
    def value(self):
        if self.__value is not None:
            return self.__value
        else:
            raise ValueError("No value")

    @property
    def error(self):
        if self.__value is None:
            return self.__error
        else:
            raise ValueError("No error")

    def unwrap(self):
        if self.__value is None:
            raise ValueError(self.__error)
        return self.__value
