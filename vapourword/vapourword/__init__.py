import sys
import os
import functools
from string import punctuation
from vapourword.plugins import Plugins


Plugins.register_types('input', 'output', 'split', 'filter', 'weight')


@Plugins.register_input
def input_file(arg):
    def input():
        return open(arg).read()
    return input

@Plugins.register_input
def input_stdin(arg):
    def input():
        return sys.stdin.read()
    return input


@Plugins.register_output
def output_stdout(arg):
    def output(data):
        for word, weight in data:
            print word, weight
    return output

@Plugins.register_output
def output_file(arg):
    def output(data):
        fh = open(arg, 'w')
        for word, weight in data:
            print >>fh, word, weight
    return output


@Plugins.register_split
def split_word(arg):
    def split(input):
        return input.split(arg)
    return split


@Plugins.register_filter
def filter_common_words(arg):
    def filt(input):
        ret = []
        for item in input:
            item = item.strip(punctuation)
            if not item: 
                continue
            ret.append(item)
        return ret
    return filt


@Plugins.register_weight
def weight_occurance(arg):
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
    )

    parser.add_option("-m", "--plugin-module",
            dest="plugin_modules",
            default=[],
            action="append",
            metavar="MODULE",
    )

    (options, args) = parser.parse_args(args)

    plugin_modules = []

    # do we want to save and restore sys.path?
    # dont think it matters much 
    sys.path.insert(0, options.plugin_paths)
    for name in options.plugin_modules:
        mod = __import__(
                name, 
                globals(), 
                locals(), 
                fromlist=[name.split('.')[-1]], 
                level=0,
        )
        plugin_modules.append(mod)

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
            return None

    input_plugin = get_plugin('input', options.input_plugin)
    output_plugin = get_plugin('output', options.output_plugin)
    split_plugin = get_plugin('split', options.split_plugin)
    filter_plugin = get_plugin('filter', options.filter_plugin)
    weight_plugin = get_plugin('weight', options.weight_plugin)

    input = input_plugin()
    data = vapourword(
            input, 
            split_plugin,
            filter_plugin,
            weight_plugin,
    )
    output_plugin(data)


if __name__ == '__main__':
    run()

   
