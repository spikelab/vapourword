import functools

class Plugins(object):
    """ just a class to hold a list of different types of plugins """
    all = {}
    
    @classmethod
    def register_type(cls, typ):
        """ register a new type of plugin - adds a helper function
        to be used as a decorator with the name "register_<typ>"
        """
        cls.all[typ] = {}
        setattr(cls, 'register_%s' % typ, functools.partial(cls.register, typ))

    @classmethod
    def register_types(cls, *types):
        """ register several types at once """
        map(cls.register_type, types)

    @classmethod
    def register(cls, typ, f):
        """ register a function as a plugin - you dont need to call this
        use register_<typ> instead 
        """
        name = f.__name__
        if name.startswith(typ+'_'):
            name = name[len(typ)+1:]
        cls.all[typ][name] = f
        return f
