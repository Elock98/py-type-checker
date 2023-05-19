from functools import wraps
from pydoc import locate
import inspect

def typecheck(*check_args):
    """
        Checks that arguments passed to function
        is of the type passed to the typechecker.
    """

    def get_fn_param(fn):
        return str(inspect.signature(fn)).replace("(", "").replace(")", "").split(",")

    def wrapper(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            if not callable(check_args[0]):
                """ Check types """
                assert len(check_args) >= (len(args)+len(kwargs)), \
                        f"TypecheckError: Cannot check all arguments given, not enough typecheck args given"
                # Check args
                for index, arg in enumerate(args):
                    if check_args[index] == 'callable':
                        assert callable(arg), \
                            f"TypeError: {arg} is of type {type(arg)}, not of type callable"
                    else:
                        if not isinstance(check_args[index], list):
                            arg_type = locate(check_args[index]) # Convert check arg string to type
                        else:
                            arg_type = check_args[index][0]
                        assert isinstance(arg, arg_type), \
                            f"TypeError: {arg} is of type {type(arg)}, not of type {arg_type}"

                # Check kwargs
                parameters = get_fn_param(func)
                parameters = [param.strip() for param in parameters]
                for param, value in kwargs.items():
                    if param in parameters:
                        if check_args[parameters.index(param)] == "callable":
                            assert callable(value), \
                                f"TypeError: {arg} is of type {type(arg)}, not of type callable"
                        else:
                            if not isinstance(check_args[parameters.index(param)], list):
                                kwarg_type = locate(check_args[parameters.index(param)])
                            else:
                                kwarg_type = check_args[parameters.index(param)][0]
                            assert isinstance(value, kwarg_type), \
                                 f"TypeError: {kwargs[param]} is of type {type(kwargs[param])}, not of type {kwarg_type}"

            return func(*args, **kwargs)
        return new_func

    # Convert input to managable type
    #
    # If no types given, leave as it is;
    # If class insert into sub-list;
    # If function set to callable check;
    # Else send primitive type as string;
    check_args = [arg if str(arg).startswith("<function") else \
            [arg] if str(arg).startswith("<class '__main__.") else \
            'callable' if str(arg) == '<built-in function callable>' else \
            str(arg).replace("<class '", "").replace("'>", "") for arg in check_args]

    if callable(check_args[0]):
        return wrapper(check_args[0])
    else:
        return wrapper
