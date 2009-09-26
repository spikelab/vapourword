import vapourword

# simple plugin
@vapourword.Plugins.register_input
def input_test(args):
    def input():
        return "blah blah boo"
    return input 


# class based plugin 
@vapourword.Plugins.register_input
class input_test3(object):
    def __init__(self, arg):
        self.arg = arg 
    
    def __call__(self):
        return "1 2 2 3 3 3 4 4 4 4"
