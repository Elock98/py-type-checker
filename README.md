# Python type-checker
This is a simple type-checker decorator for python that
can be used to ensure that the correct type is passed to functions.

## Example

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

The type-checker can also check if argument is a function

```
from typechecker import typecheck

def foo():
    pass

@typecheck(callable)
def bar(fn):
    pass

bar(fn=foo)
```

It can also check user defined types

```
from typechecker import typecheck

class Foo:
    pass

@typecheck(Foo)
def bar(obj):
    pass

bar(Foo())
```
