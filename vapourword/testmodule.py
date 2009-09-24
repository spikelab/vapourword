import vapourword

@vapourword.Plugins.register_input
def input_test(args):
    def input():
        return "blah blah boo"
    return input 

