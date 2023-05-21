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
