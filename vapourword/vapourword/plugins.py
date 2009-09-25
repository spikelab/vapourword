import sys
import functools

class Plugins(object):
    """ just a class to hold a list of different types of plugins """

    all = {}

    # probably dont need this but what the hell...
    plugin_modules = []

    class PluginException(Exception):
        """ base exception for plugins """
        pass

    class ArgumentError(PluginException):
        pass

    
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

    @classmethod
    def load_modules(cls, modules, paths=None):
        """ import the modules `modules`. if paths is specified this 
        is first inserted at the beginning of sys.path """
        # do we want to save and restore sys.path?
        # dont think it matters much ...
        if paths:
            # FIXME should prob check for duplicates
            sys.path = paths + sys.path

        for name in modules:
            mod = __import__(
                    name, 
                    globals(), 
                    locals(), 
                    fromlist=[name.split('.')[-1]], 
                    level=0,
            )
            cls.plugin_modules.append(mod)
