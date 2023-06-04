import unittest
from typechecker import typecheck, TypeCheckError

class TestTypeChecker(unittest.TestCase):

    def test_no_checks(self):
        # Given
        @typecheck # No typechecks given
        def foo(bar):
            return bar

        # When
        res = foo(5)

        # Then
        self.assertEqual(res, 5)

    def test_check_args(self):
        # Given
        @typecheck(int)
        def foo(bar):
            return bar

        # When
        res = foo(5)

        # Then
        self.assertEqual(res, 5)

    def test_check_kwargs(self):
        # Given
        @typecheck(bar=int)
        def foo(bar):
            return bar

        # When
        res = foo(5)

        # Then
        self.assertEqual(res, 5)

    def test_bad_check_kwargs(self):
        # Given
        @typecheck(baz=int)
        def foo(bar):
            return bar

        # When
        with self.assertRaises(TypeCheckError) as e:
            res = foo(5)

        # Then
        self.assertTrue(str(e.exception).startswith("The given kwarg baz "\
                "is not a parameter of function <function TestTypeChecker."\
                "test_bad_check_kwargs.<locals>.foo at"))

    def test_check_multiple_kwargs(self):
        # Given
        @typecheck(baz=int, bar=str)
        def foo(bar, baz):
            return (bar, baz)

        # When
        res = foo("1", baz=5)

        # Then
        self.assertEqual(res, ("1", 5))

    def test_check_nonetype(self):
        # Given
        @typecheck(None, int)
        def foo(n, i):
            return i

        # When
        res = foo(None, 5)

        # Then
        self.assertEqual(res, 5)

    def test_check_no_nonetype(self):
        # Given
        @typecheck(None, int)
        def foo(n, i):
            return i

        # When
        with self.assertRaises(TypeError) as exep:
            foo(6, 5)

        # Then
        self.assertEqual(str(exep.exception),
                "The value 6 sent to parameter n of function foo "\
                "is of type <class 'int'>, expected type <class 'NoneType'>")

    def test_ignore(self):
        # Given
        @typecheck("pass")
        def foo(bar):
            return bar

        # When
        res = foo(3)

        # Then
        self.assertEqual(res, 3)

    def test_ignore_some(self):
        # Given
        @typecheck(int, "pass", str)
        def foo(faz, bar, baz):
            return (faz, bar, baz)

        # When
        res = foo(1, 3.5**2, "FOO")

        # Then
        self.assertEqual(res, (1, 3.5**2, "FOO"))

    def test_ignore_kwarg(self):
        # Given
        @typecheck("pass")
        def foo(bar):
            return bar

        # When
        res = foo(bar=3)

        # Then
        self.assertEqual(res, 3)

    def test_ignore_some_kwarg(self):
        # Given
        @typecheck(int, "pass", str)
        def foo(faz, bar, baz):
            return (faz, bar, baz)

        # When
        res = foo(baz="FOO", faz=1, bar=3.5**2)

        # Then
        self.assertEqual(res, (1, 3.5**2, "FOO"))

    def test_multiple_options_arg(self):
        # Given
        class Foo:
            pass

        @typecheck(int, str, (Foo, int, float))
        def bar(a, b, c):
            return (type(a), type(b), type(c))

        # When
        res1 = bar(1, "2", 3.4)
        res2 = bar(1, "2", 3)
        res3 = bar(1, "2", Foo())

        with self.assertRaises(TypeError) as exep:
            bar(1, "2", "FOO")

        # Then
        self.assertEqual(res1, (int, str, float))
        self.assertEqual(res2, (int, str, int))
        self.assertEqual(res3, (int, str, Foo))
        self.assertEqual(str(exep.exception),
                "The value FOO sent to "\
                "parameter c of function bar is of type <class 'str'>, "\
                "expected type "\
                "(<class '__main__.TestTypeChecker.test_multiple_options_arg.<locals>.Foo'>, "\
                "<class 'int'>, <class 'float'>)")

    def test_multiple_options_kwarg(self):
        # Given
        class Foo:
            pass

        @typecheck(int, str, (Foo, int, float))
        def bar(a, b, c):
            return (type(a), type(b), type(c))

        # When
        res1 = bar(c=3.4, a=1, b="2")
        res2 = bar(c=1, a=1, b="2")
        res3 = bar(c=Foo(), a=1, b="2")

        with self.assertRaises(TypeError) as exep:
            bar(c="FOO", a=1, b="2")

        # Then
        self.assertEqual(res1, (int, str, float))
        self.assertEqual(res2, (int, str, int))
        self.assertEqual(res3, (int, str, Foo))
        self.assertEqual(str(exep.exception),
                "The value FOO sent to "\
                "parameter c of function bar is of type <class 'str'>, "\
                "expected type "\
                "(<class '__main__.TestTypeChecker.test_multiple_options_kwarg.<locals>.Foo'>, "\
                "<class 'int'>, <class 'float'>)")

    def test_multiple_options_arg_ignore(self):
        # Given
        class Foo:
            pass

        @typecheck(int, str, (Foo, "pass", float))
        def bar(a, b, c):
            return (type(a), type(b), type(c))

        # When
        res1 = bar(1, "2", 3.4)
        res2 = bar(1, "2", 3)
        res3 = bar(1, "2", Foo())
        res4 = bar(1, "2", "3")

        # Then
        self.assertEqual(res1, (int, str, float))
        self.assertEqual(res2, (int, str, int))
        self.assertEqual(res3, (int, str, Foo))
        self.assertEqual(res4, (int, str, str))


    def test_multiple_options_kwarg_ignore(self):
        # Given
        class Foo:
            pass

        @typecheck(int, str, (Foo, "pass", float))
        def bar(a, b, c):
            return (type(a), type(b), type(c))

        # When
        res1 = bar(c=3.4, a=1, b="2")
        res2 = bar(c=1, a=1, b="2")
        res3 = bar(c=Foo(), a=1, b="2")
        res4 = bar(c="3", a=1, b="2")

        # Then
        self.assertEqual(res1, (int, str, float))
        self.assertEqual(res2, (int, str, int))
        self.assertEqual(res3, (int, str, Foo))
        self.assertEqual(res4, (int, str, str))

    def test_check_expression(self):
        # Given
        @typecheck(int, float)
        def foo(i, f):
            return (i, f)

        # When
        res = foo(1+3, 5/3)

        # Then
        self.assertEqual(res, (1+3, 5/3))

    def test_check_args_type_err(self):
        # Given
        @typecheck(int)
        def foo(bar):
            return bar

        # When
        with self.assertRaises(TypeError) as exep:
            res = foo("5")

        # Then
        self.assertEqual(str(exep.exception),
                "The value 5 sent to parameter bar of function foo "\
                "is of type <class 'str'>, expected type <class 'int'>")

    def test_not_enough_check_args(self):
        # Given
        @typecheck(int)
        def foo(bar, baz):
            return (bar, baz)

        # When
        res = foo(1, 2)

        # Then
        self.assertEqual(res, (1, 2))

    def test_to_many_check_args(self):
        # Given
        @typecheck(int, int)
        def foo(bar):
            return (bar)

        # When
        res = foo(1)

        # Then
        self.assertEqual(res, 1)

    def test_multiple_arguments_check(self):
      # Given
      @typecheck(int, str, float)
      def foo(bar, baz, faz):
          return (bar, baz, faz)

      # When
      res = foo(1, "2", 4.3)

      # Then
      self.assertEqual(res, (1, "2", 4.3))

    def test_function_as_argument(self):
        # Given
        def foo():
            return "FOO"

        @typecheck(callable)
        def bar(fn):
            return fn()

        # When
        res = bar(foo)

        # Then
        self.assertEqual(res, "FOO")

    def test_function_as_kwarg(self):
        # Given
        def foo():
            return "FOO"

        @typecheck(callable)
        def bar(fn):
            return fn()

        # When
        res = bar(fn=foo)

        # Then
        self.assertEqual(res, "FOO")

    def test_lambda_as_arg(self):
        # Given
        @typecheck(callable)
        def foo(fn):
            return fn(5)

        # When
        res = foo(lambda x: x**2)

        # Then
        self.assertEqual(res, 25)

    def test_class_instance_as_argument(self):
        # Given
        class Foo:
            def __init__(self, faz):
                self.faz = faz

            def get_faz(self):
                return self.faz

        foo = Foo("FAZ")

        @typecheck(Foo)
        def bar(obj):
            return obj.get_faz()

        # When
        res = bar(foo)

        # Then
        self.assertEqual(res, "FAZ")

    def test_class_instance_as_kwarg(self):
        # Given
        class Foo:
            def __init__(self, faz):
                self.faz = faz

            def get_faz(self):
                return self.faz

        foo = Foo("FAZ")

        @typecheck(Foo)
        def bar(obj):
            return obj.get_faz()

        # When
        res = bar(obj=foo)

        # Then
        self.assertEqual(res, "FAZ")

    def test_class_instance_inheritance(self):
        # Given
        class Foo:
            def get_val(self):
                return 5

        class Faz(Foo):
            pass

        faz = Faz()

        @typecheck(Foo)
        def bar(obj):
            return obj.get_val()

        # When
        res = bar(obj=faz)

        # Then
        self.assertEqual(res, 5)

    def test_wrong_class_instance_as_argument(self):
        # Given
        class Foo:
            pass

        class Baz:
            pass

        foo = Foo()

        @typecheck(Baz)
        def bar(obj):
            return obj.get_faz()

        # When
        with self.assertRaises(TypeError) as exep:
            bar(foo)

        # Then
        self.assertRegex(str(exep.exception), \
                "The value <__main__.TestTypeChecker.test_wrong_class_instance_as_argument.<locals>.Foo "\
                "object at .*> sent to parameter obj of function bar is of type "\
                "<class '__main__.TestTypeChecker.test_wrong_class_instance_as_argument.<locals>.Foo'>, "\
                "expected type <class '__main__.TestTypeChecker.test_wrong_class_instance_as_argument.<locals>.Baz'>")

    def test_check_instance_method_args(self):
        # Given
        class Foo:
            @typecheck("pass", int)
            def bar(self, i):
                return i

        foo = Foo()

        # When
        res = foo.bar(5)

        # Then
        self.assertEqual(res, 5)


    def test_check_class_method_args(self):
        # Given
        class Foo:
            @classmethod
            @typecheck("pass", int)
            def bar(self, i):
                return i

        foo = Foo()

        # When
        res = foo.bar(5)

        # Then
        self.assertEqual(res, 5)

    def test_check_instance_method_kwargs(self):
        # Given
        class Foo:
            @typecheck("pass", int)
            def bar(self, i):
                return i

        foo = Foo()

        # When
        res = foo.bar(i=5)

        # Then
        self.assertEqual(res, 5)

    def test_check_class_method_kwargs(self):
        # Given
        class Foo:
            @classmethod
            @typecheck("pass", int)
            def bar(self, i):
                return i

        foo = Foo()

        # When
        res = foo.bar(i=5)

        # Then
        self.assertEqual(res, 5)

    def test_kwargs_ordered(self):
        # Given
        @typecheck(int, str)
        def foo(bar, baz):
            return (bar, baz)

        # When
        res = foo(bar=1, baz="2")

        # Then
        self.assertEqual(res, (1, "2"))

    def test_kwargs_ordered_err(self):
        # Given
        @typecheck(int, str)
        def foo(bar, baz):
            return (bar, baz)

        # When
        with self.assertRaises(TypeError) as exep:
            res = foo(bar=1, baz=2)

        # Then
        self.assertEqual(str(exep.exception),
                "The value 2 sent to parameter baz of function foo "\
                        "is of type <class 'int'>, expected type <class 'str'>")


    def test_kwargs_unordered(self):
        # Given
        @typecheck(int, str)
        def foo(bar, baz):
            return (bar, baz)

        # When
        res = foo(baz="1", bar=2)

        # Then
        self.assertEqual(res, (2, "1"))

    def test_kwargs_unordered_err(self):
        # Given
        @typecheck(int, str)
        def foo(bar, baz):
            return (bar, baz)

        # When
        with self.assertRaises(TypeError) as exep:
            res = foo(baz=1, bar=2)

        # Then
        self.assertEqual(str(exep.exception),
                "The value 1 sent to parameter baz of function foo "\
                "is of type <class 'int'>, expected type <class 'str'>")


    def test_list_as_argument(self):
        # Given
        lst = [1, 4.2, "foo"]

        @typecheck(list)
        def foo(ls):
            return ls[-1]

        # When
        res = foo(lst)

        # Then
        self.assertEqual(res, "foo")

    def test_tuple_as_argument(self):
        # Given
        tpl = (1, 4.2, "foo")

        @typecheck(tuple)
        def foo(tp):
            return tp[-1]

        # When
        res = foo(tpl)

        # Then
        self.assertEqual(res, "foo")

    def test_dictionary_as_argument(self):
        # Given
        dct = {
                "foo" : 1,
                "bar" : 4.2,
                "baz" : lambda x: x-5
              }

        @typecheck(dict)
        def foo(dc):
            return dc["foo"]

        # When
        res = foo(dct)

        # Then
        self.assertEqual(res, 1)

    def test_list_as_kwarg(self):
        # Given
        lst = [1, 4.2, "foo"]

        @typecheck(list)
        def foo(ls):
            return ls[-1]

        # When
        res = foo(ls=lst)

        # Then
        self.assertEqual(res, "foo")

    def test_tuple_as_kwarg(self):
        # Given
        tpl = (1, 4.2, "foo")

        @typecheck(tuple)
        def foo(tp):
            return tp[-1]

        # When
        res = foo(tp=tpl)

        # Then
        self.assertEqual(res, "foo")

    def test_dictionary_as_kwarg(self):
        # Given
        dct = {
                "foo" : 1,
                "bar" : 4.2,
                "baz" : lambda x: x-5
              }

        @typecheck(dict)
        def foo(dc):
            return dc["foo"]

        # When
        res = foo(dc=dct)

        # Then
        self.assertEqual(res, 1)

    def test_non_set_check_args(self):
        # Given
        @typecheck(int, float)
        def foo(a, b, c):
            return (a, b, c)

        # When
        res = foo(1, 2.3, "4")

        # Then
        self.assertEqual(res, (1, 2.3, "4"))

    def test_non_set_check_kwargs(self):
        # Given
        @typecheck(a=int, c=str)
        def foo(a, b, c):
            return (a, b, c)

        # When
        res = foo(1, 2.3, "4")

        # Then
        self.assertEqual(res, (1, 2.3, "4"))


    def test_set_same_arg_with_kwarg(self):
        # Given
        @typecheck(int, a=str)
        def foo(a, b):
            pass

        # When
        with self.assertRaises(TypeCheckError) as e:
            foo(1, 3)

        # Then
        self.assertEqual(str(e.exception), "The kwarg a is already set by arg")

if __name__ == "__main__":
    unittest.main()
