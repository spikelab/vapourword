import sys
import os
import functools
from string import punctuation
from vapourword.plugins import Plugins


Plugins.register_types('input', 'output', 'split', 'filter', 'weight')


@Plugins.register_input
def input_file(arg):
    """ read input from a file """

    if not arg:
        raise Plugins.ArgumentError("file input plugin needs a filename argument")

    def input():
        return open(arg).read()
    return input

@Plugins.register_input
def input_stdin(arg):
    """ read input from stdin """
    def input():
        return sys.stdin.read()
    return input


@Plugins.register_output
def output_stdout(arg):
    """ output results to stdout """
    def output(data):
        for word, weight in data:
            print word, weight
    return output

@Plugins.register_output
def output_file(arg):
    """ output results to a file """

    if not arg:
        raise Plugins.ArgumentError("file output plugin needs a filename argument")

    def output(data):
        fh = open(arg, 'w')
        for word, weight in data:
            print >>fh, word, weight
    return output


@Plugins.register_split
def split_word(arg):
    """ split input by white space """
    def split(input):
        return input.split(arg)
    return split

common_words = set("a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your".split(','))

@Plugins.register_filter
def filter_common_words(arg):
    """ filter common words out """
    def filt(input):
        ret = []
        for item in input:
            item = item.strip(punctuation)
            if not item or item in common_words: 
                continue
            ret.append(item)
        return ret
    return filt


@Plugins.register_weight
def weight_occurance(arg):
    """ weigh input by occurance """
    def weight(input):
        items = {}
        for item in input:
            items[item] = items.get(item, 0) + 1
        return items.items()
    return weight


def vapourword(input, split_func, filter_func, weight_func):
    if split_func:
        input = split_func(input)
    if filter_func:
        input = filter_func(input)
    return weight_func(input)


def run(args=None):
    """ console app entry point """

    import imp
    import optparse

    parser = optparse.OptionParser()
    parser.add_option("-i", "--input-plugin", 
            dest="input_plugin", 
            default="stdin", 
            metavar="PLUGIN[:ARG]",
    )
    parser.add_option("-o", "--output-plugin", 
            dest="output_plugin", 
            default="stdout", 
            metavar="PLUGIN[:ARG]",
    )
    parser.add_option("-s", "--split-plugin", 
            dest="split_plugin", 
            default="word", 
            metavar="PLUGIN[:ARG]",
    )
    parser.add_option("-f", "--filter-plugin", 
            dest="filter_plugin", 
            default="common_words", 
            metavar="PLUGIN[:ARG]",
    )
    parser.add_option("-w", "--weight-plugin", 
            dest="weight_plugin", 
            default="occurance", 
            metavar="PLUGIN[:ARG]",
    )

    parser.add_option("-d", "--plugin-path",
            dest="plugin_paths",
            default=[],
            action="append",
            metavar="PATH",
            help="extra paths to search when loading plugins - you can specify this option more than once",
    )

    parser.add_option("-m", "--plugin-module",
            dest="plugin_modules",
            default=[],
            action="append",
            metavar="MODULE",
            help="extra modules to load plugins from - you can specify this option more than once",
    )

    parser.add_option("-L", "--list-plugins", 
            dest="list_plugins",
            default=False,
            action="store_true",
    )
      

    (options, args) = parser.parse_args(args)

    # load any modules specified on the command line 
    Plugins.load_modules(options.plugin_modules, paths=options.plugin_paths)

    # print a list of plugins 
    if options.list_plugins:
        for typ in sorted(Plugins.all.keys()):
            print "%s:" % typ
            for name in sorted(Plugins.all[typ].keys()):
                print "    %s" % name, 
                f = Plugins.all[typ][name].__doc__
                if f:
                    print "- %s" % f.split('\n')[0].strip()
                else:
                    print 
        return 

    # not quite sure on the best way to pass arguments to plugins 
    # so this lets you do 
    # -<opt> <plugin>:arg_string
    # arg string will be passed to the plugin function 
    def get_plugin(typ, s):
        p = s.split(':', 1)
        plugin = p[0]
        if len(p) == 2:
            arg = p[1]
        else:
            arg = None
            
        func = Plugins.all[typ].get(plugin)
        if func:
            return func(arg)
        else:
            print >>sys.stderr, "%s plugin %s not found" % (typ, plugin)
            return None

    # get all our functions ready to do stuff - we'll have 
    # the inner functions of the plugins here - or None if the plugin 
    # wasnt found/loaded  

    funcs = {}

    for name in ('input', 'output', 'split', 'filter', 'weight'):
        try:
            funcs[name] = get_plugin(name, getattr(options, '%s_plugin' % name))
        except Plugins.ArgumentError, e:
            print >>sys.stderr, "%s: %s" % (type(e).__name__, str(e))
            return 1
        if name not in ('split', 'filter') and funcs[name] is None:
            print >>sys.stderr, "%s plugin cannot be None" % name
            return 1

    # actually do stuff 
    funcs['output'](vapourword(
            funcs['input'](),
            funcs['split'],
            funcs['filter'],
            funcs['weight'],
    ))


if __name__ == '__main__':
    sys.exit(run())

   
