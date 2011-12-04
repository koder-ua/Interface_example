import unittest
import contextlib

from oktest import ok, test

from interfaces import Interface, ImplementsBase, \
                       check_signature_acceptable, do_check_me, do_not_check_me

def not_check_signature_acceptable(iface_func, impl_func):
    try:
        check_signature_acceptable(iface_func, impl_func)
    except AssertionError:
        pass
    else:
        raise AssertionError("{1} have acceptable to {0} interface".
                        format(impl_func, iface_func))

@contextlib.contextmanager
def raises(exc_tp):
    try:
        yield None
    except exc_tp:
        pass
    else:
        raise AssertionError("Exception %s haven't raised" % exc_tp)

class InterfaceTester(unittest.TestCase):

    @test("function interface compatibility")
    def test_func_iface(self):
        def intr(a, b, c):
            pass

        def impl1(a, b, c, d):
            pass
        not_check_signature_acceptable(intr, impl1)

        def impl2(a, b, c, d=12):
            pass
        check_signature_acceptable(intr, impl2)

        def impl3(a, b, *dt):
            pass
        not_check_signature_acceptable(intr, impl3)

        def impl4(a, b, *dt, **mp):
            pass
        check_signature_acceptable(intr, impl4)

        def impl5(a, b, c=13):
            pass
        check_signature_acceptable(intr, impl5)

        def impl6(a, b, c, *dt):
            pass
        check_signature_acceptable(intr, impl6)

        def impl7(a, b, c, **mp):
            pass
        check_signature_acceptable(intr, impl7)
                
        def impl8(*dt, **mp):
            pass
        check_signature_acceptable(intr, impl8)
                
        def impl9(a, b, d):
            pass
        not_check_signature_acceptable(intr, impl9)
                
        def impl10(a, b):
            pass
        not_check_signature_acceptable(intr, impl10)
                
        def impl11(c, e):
            pass
        not_check_signature_acceptable(intr, impl11)

        def intr2():
            pass
        def impl12():
            pass
        check_signature_acceptable(intr2, impl12)

        def intr3():
            pass
        def impl13(*dt, **mp):
            pass
        check_signature_acceptable(intr3, impl13)

        def intr4(*dt):
            pass
        def impl14(*dt, **mp):
            pass
        check_signature_acceptable(intr4, impl14)

        def intr5(*dt, **mp):
            pass
        def impl15(*dt, **mp):
            pass
        check_signature_acceptable(intr5, impl15)

        def intr6(*dt, **mp):
            pass
        def impl16(**mp):
            pass
        not_check_signature_acceptable(intr6, impl16)

        def intr7(*dt, **mp):
            pass
        def impl17():
            pass
        not_check_signature_acceptable(intr7, impl17)
                
        def intr8(*dt, **mp):
            pass
        def impl18(p, f=12):
            pass
        not_check_signature_acceptable(intr8, impl18)

        def intr9(*dt, **mp):
            pass
        def impl19(p, *dt, **mp):
            pass
        not_check_signature_acceptable(intr9, impl19)

        def intr10(*dt, **mp):
            pass
        def impl20(p=12, *dt, **mp):
            pass
        check_signature_acceptable(intr10, impl20)

    @test("simple implementation")
    def test1(self):
        class MyInterface(Interface):
            def func(x, y, z):
                pass
        
        class Impl(ImplementsBase):
            __implements__ = [MyInterface]
            def func(self, x, y, z=13):
                pass
    
    @test("wrong implementation1")
    def test2(self):
        class MyInterface(Interface):
            def func(x, y, z):
                pass
        
        with raises(AssertionError):
            class Impl(ImplementsBase):
                __implements__ = [MyInterface]
                def func(self, x, y):
                    pass

    @test("not all methods implemented")
    def test3(self):
        class MyInterface(Interface):
            def func(x, y, z):
                pass

            def func2(x):
                pass
        
        with raises(AssertionError):
            class Impl(ImplementsBase):
                __implements__ = [MyInterface]
                def func(self, x, y, z):
                    pass

    @test("wrong base implementation")
    def test4(self):
        class MyInterface(Interface):
            def func(x, y, z):
                pass

            def func2(x):
                pass
        
        class ImplFirstFunc(object):
            def func2(self, x, y):
                pass
           
        with raises(AssertionError):
            class Impl(ImplementsBase, ImplFirstFunc):
                __implements__ = [MyInterface]
                def func(self, x, y, z):
                    pass

    @test("all methods implemented")
    def test5(self):
        class MyInterface(Interface):
            def func(x, y, z):
                pass

            def func2(x):
                pass
        
        class ImplFirstFunc(object):
            def func2(self, x):
                pass
           
        class Impl(ImplementsBase, ImplFirstFunc):
            __implements__ = [MyInterface]
            def func(self, x, y, z):
                pass

    @test("check acceptable set of interfaces")
    def test5(self):
        class MyInterface1(Interface):
            def func(x, y, z):
                pass

        class MyInterface2(Interface):
            def func2(x):
                pass
        
        with raises(AssertionError):
            class Impl(ImplementsBase):
                __implements__ = [MyInterface1, MyInterface2]
                def func(self, x, y, z):
                    pass

        class Impl(ImplementsBase):
            __implements__ = [MyInterface1, MyInterface2]
            def func(self, x, y, z):
                pass

            def func2(self, x):
                pass

    @test("check unacceptable set of interfaces")
    def test5(self):
        class MyInterface1(Interface):
            def func(x, y, z):
                pass

        class MyInterface2(Interface):
            def func(x):
                pass

        with raises(AssertionError):
            class Impl(ImplementsBase):
                __implements__ = [MyInterface1, MyInterface2]
                def func(self, x, y, z):
                    pass
    
    @test("check parameters")
    def test6(self):
        class MyInterface(Interface):
            def func(x, y, z):
                ok(x).is_a(int)
                ok(y).is_a(str)
                ok(z).is_a(int) > x

        class Impl(ImplementsBase):
            __implements__ = [MyInterface]
            def func(self, x, y, z):
                pass
        
        obj = Impl()

        obj.func(1, "ff", 2)

        with raises(AssertionError):
            obj.func("f", "ff", 1)

        with raises(AssertionError):
            obj.func(1, 1, 1)

    @test("check parameters with self")
    def test7(self):
        class MyInterface(Interface):
            def func(self, x, y, z):
                ok(x).is_a(int)
                ok(y).is_a(str)
                ok(z).is_a(int) > x

        class Impl(ImplementsBase):
            __implements__ = [MyInterface]
            def func(self, x, y, z):
                pass
        
        obj = Impl()

        obj.func(1, "ff", 2)

        with raises(AssertionError):
            obj.func("f", "ff", 1)

        with raises(AssertionError):
            obj.func(1, 1, 1)


    @test("check parameters and res")
    def test8(self):
        class MyInterface(Interface):
            def func(self, x, y, z):
                ok(x).is_a(int)
                ok(y).is_a(str)
                ok(z).is_a(int) > x
                res = yield
                ok(res).is_a(int)

        class Impl(ImplementsBase):
            __implements__ = [MyInterface]
            def func(self, x, y, z):
                return 12
        
        obj = Impl()

        obj.func(1, "ff", 2)

    @test("check inherited methods guarded")
    def test9(self):
        class MyInterface(Interface):
            def func(self, x, y, z):
                ok(x).is_a(int)
                ok(y).is_a(str)
                ok(z).is_a(int) > x
                res = yield
                ok(res).is_a(int)

        class MeBase(object):
            def func(self, x, y, z):
                return 12

        class Impl(MeBase, ImplementsBase):
            __implements__ = [MyInterface]
        
        obj = Impl()

        obj.func(1, "ff", 2)

        with raises(AssertionError):
            obj.func("f", "ff", 1)

        with raises(AssertionError):
            obj.func(1, 1, 1)


    @test("check inherited from implementations methods guarded")
    def test10(self):
        class MyInterface(Interface):
            def func(self, x, y, z):
                ok(x).is_a(int)
                ok(y).is_a(str)
                ok(z).is_a(int) > x
                res = yield
                ok(res).is_a(int)

        class MyInterface2(Interface):
            def func2(x):
                ok(x).is_a(float)

        class MeBase(ImplementsBase):
            __implements__ = [MyInterface]
            def func(self, x, y, z):
                return 12

        class Impl(MeBase, ImplementsBase):
            __implements__ = [MyInterface2]
            def func2(self, x):
                return None
        
        obj = Impl()

        obj.func(1, "ff", 2)
        obj.func2(1.2)
        
        with raises(AssertionError):
            obj.func("f", "ff", 1)

        with raises(AssertionError):
            obj.func(1, 1, 1)

        with raises(AssertionError):
            obj.func2(None)

    def test_after_init_check(self):
        class MyInterface(Interface):
            @classmethod
            def __after_init_check__(cls, tp):
                ok(tp).has_attr('priority')        
                ok(tp.priority).is_a(int) > 0
                ok(tp.priority) < 100

        with raises(AssertionError):
            class Impl(ImplementsBase):
                __implements__ = [MyInterface]
    
        with raises(AssertionError):
            class Impl(ImplementsBase):
                __implements__ = [MyInterface]
                priority = None

        with raises(AssertionError):
            class Impl(ImplementsBase):
                __implements__ = [MyInterface]
                priority = -217

        class Impl(ImplementsBase):
            __implements__ = [MyInterface]
            priority = 15

    @test("bug in check function")
    def test_wrong_check_func(self):
        class MyInterface(Interface):
            def func(self, x, y, z):
                yield
                yield 1

        class Impl(ImplementsBase):
            __implements__ = [MyInterface]
            def func(self, x, y, z):
                return 12
        
        obj = Impl()

        with raises(AssertionError):
            obj.func(1, "ff", 2)

    @test("special method")
    def test_special_methods(self):
        class MyInterface(Interface):
            def __str__(self):
                return "MyInterface"
            
            def __my_special_method__(self):
                pass

            @do_check_me
            def __len__(self):
                res = yield
                ok(res) > 0
            
            @do_not_check_me
            def some_func(self):
                pass
        
        with raises(AssertionError):
            class Impl(ImplementsBase):
                __implements__ = [MyInterface]
                def some_func(self):
                    pass

        class Impl(ImplementsBase):
            __implements__ = [MyInterface]
            def __len__(self):
                return 10
        
        len(Impl())
        Impl().__len__()

        with raises(AssertionError):
            class Impl(ImplementsBase):
                __implements__ = [MyInterface]
                def __len__(self):
                    return -10
            len(Impl())


if __name__ == '__main__':
    unittest.main()




