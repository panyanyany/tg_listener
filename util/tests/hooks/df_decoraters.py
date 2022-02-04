
from util.hooks.decoraters import return_hooker

class Test(object):

    def foo(self, *args):
        return args


def test_return_hooks():
    hooks = return_hooker(Test.foo)
    t = Test()
    hooks = return_hooker(t.foo)
