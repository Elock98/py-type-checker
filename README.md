# Python type-checker
This is a simple type-checker decorator for python that
can be used to ensure that the correct type is passed to functions.

## Usage
1. Basic Usage
2. Ignore Option
3. Multiple Options
4. Functions as Arguments
5. Class instance as Arguments
6. Checking Class and Instance Methods
7. Checking Return Type
8. Type Hints and Default Values

### Basic Usage

```
from typechecker import typecheck

# example without type-checker decorator

def foo(bar, baz):
    assert isinstance(bar, int), f"The value given to bar is not type int"
    assert isinstance(baz, float), f"The value given to baz is not type float"
    pass

# the same example using the type-checker decorator

@typecheck(int, float)
def foo(bar, baz):
    pass

```

Note that you can also set checks using keyword arguments.

```
from typechecker import typecheck

@typecheck(baz=float, bar=int)
def foo(bar, baz):
    pass
```

### Ignore Option

```
from typechecker import typecheck

@typecheck(int, 'pass', str)
def foo(a, b, c):
    pass
```

Doing this will type-check the values
passed to 'a' and 'c', and ignore checking
the value passed to 'b'.

Note that it no longer is necessary to
explicitly set a parameter to 'pass'
(see examples below), since this is
done automatically.

```
from typechecker import typecheck

@typecheck(int, float)
def foo(a, b, c, d):
    pass
```

and

```
from typechecker import typecheck

@typecheck(c=int, d=float)
def foo(a, b, c, d):
    pass
```

is the same as

```
from typechecker import typecheck

@typecheck(int, float, 'pass', 'pass')
def foo(a, b, c, d):
    pass
```

and

```
from typechecker import typecheck

@typecheck('pass', 'pass', int, float)
def foo(a, b, c, d):
    pass
```

### Multiple Options

```
from typechecker import typecheck

@typecheck(int, (int, float))
def foo(a, b):
    pass
```

Doing this will check that the value passed
to 'a' is an int and that the value passed
to 'b' is an int or a float.

```
from typechecker import typecheck

@typecheck(int, (int, float, 'pass'))
def foo(a, b):
    pass
```

Note that in the example above the value
passed to 'b' will not be checked.

### Functions as Arguments

```
from typechecker import typecheck

def foo():
    pass

@typecheck(callable)
def bar(fn):
    pass

bar(fn=foo)
bar(fn=lambda x: x+1)
```

### Class Instances as Arguments

```
from typechecker import typecheck

class Foo:
    pass

@typecheck(Foo)
def bar(obj):
    pass

bar(Foo())
```

### Checking Class and Instance Methods

```
from typechecker import typecheck

class Foo:
    @typecheck('pass', int)
    def bar(self, i):
        pass

    @classmethod
    @typecheck('pass', int)
    def baz(cls, i):
        pass

```

Note that when type-checking class and instance methods
you need to set the first parameter to 'pass' due to them
taking a reference to the instance or the class. Also note
that the order of decorators matter, the type-checker
needs to be the last decorator added.

### Checking Return Type

It is possible to check the return type of the function as well.

The following will work fine:

```
@typecheck(int, b=float, check_return_type=str)
def foo(a, b):
    return str(a/b)
```

```
@typecheck(int, b=float, check_return_type=(str, int))
def foo(a, b):
    return str(a/b)
```

and this will raise a TypeError:

```
@typecheck(int, b=float, check_return_type=str)
def foo(a, b):
    return a/b
```

Note that the keyword-argument 'check\_return\_type' is reserved by
the type-checker, meaning that if you want to use the type-checker
your function can't have a parameter with the same name.

### Type Hints and Default Values

Currently the type-checker ignores type hints.
This means that there can be a mismatch between the type hints and
what the type-checker expects (without any issues).

When using default values the type-checker will ignore checking
when no value is given, however if there is no default value
and no value given the type-checker will throw a TypeCheckError.
