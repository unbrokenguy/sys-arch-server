class SingletonMeta(type):
    """
    Metaclass realization of SingleTon.
    Attributes:
        _instances: A dict where class name is key and instance is value.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        When class was called "class()", checking if instance of class exists returns it,
        else class instance created with *args and **kwargs.
        Args:
            *args: positional arguments.
            **kwargs: keyword arguments.
        Returns:
            Called class instance
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
