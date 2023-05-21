from functools import wraps
from pydoc import locate
import inspect

def typecheck(*check_args, **check_kwargs):
    """
        Checks that arguments passed to function
        is of the type passed to the typechecker.
    """

    def get_fn_param(fn):
        return [param.strip() for param in str(inspect.signature(fn)).replace("(", "").replace(")", "").split(",")]

    def pass_filter(tup):
        return tup if "pass" not in tup else "pass"

    def parse_check_kwargs(fn, check_args):
        params = get_fn_param(fn)

        for index, param in enumerate(params):
            if param in check_kwargs:
                # Process and add to check_args
                check_args.insert(index, \
                    check_kwargs[param] if str(check_kwargs[param]).startswith("<function") else \
                    check_kwargs[param] if check_kwargs[param] == "pass" else \
                    pass_filter(check_kwargs[param]) if isinstance(check_kwargs[param], tuple) else \
                    [check_kwargs[param]] if str(check_kwargs[param]).startswith("<class '__main__.") else \
                    'callable' if str(check_kwargs[param]) == '<built-in function callable>' else \
                    str(check_kwargs[param]).replace("<class '", "").replace("'>", "")
                    )

    def parse_check_args(ca):
        # Convert input to managable type
        #
        # If no types given, leave as it is;
        # If class insert into sub-list;
        # If function set to callable check;
        # If string 'pass' leave it
        # If tuple leave it
        # Else send primitive type as string;
        return  [
                    arg if str(arg).startswith("<function") else \
                    arg if arg == "pass" else \
                    pass_filter(arg) if isinstance(arg, tuple) else \
                    [arg] if str(arg).startswith("<class '__main__.") else \
                    'callable' if str(arg) == '<built-in function callable>' else \
                    str(arg).replace("<class '", "").replace("'>", "") for arg in ca
                ]



    def wrapper(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            parse_check_kwargs(func, check_args)
            if not callable(check_args[0]):
                """ Check types """
                assert len(check_args) >= (len(args)+len(kwargs)), \
                        f"TypecheckError: Cannot check all arguments given, not enough typecheck args given"
                # Check args
                for index, arg in enumerate(args):
                    if check_args[index] == "pass":
                        continue
                    elif check_args[index] == 'callable':
                        assert callable(arg), \
                            f"TypeError: {arg} is of type {type(arg)}, not of type callable"
                    else:
                        if not isinstance(check_args[index], (list, tuple)):
                            arg_type = locate(check_args[index]) # Convert check arg string to type
                            if arg_type is None:
                                arg_type = type(None)
                        else:
                            if isinstance(check_args[index], list):
                                arg_type = check_args[index][0]
                            else:
                                arg_type = tuple(check_args[index])
                        assert isinstance(arg, arg_type), \
                            f"TypeError: {arg} is of type {type(arg)}, not of type {arg_type}"

                # Check kwargs
                parameters = get_fn_param(func)
                for param, value in kwargs.items():
                    if param in parameters:
                        if check_args[parameters.index(param)] == "pass":
                            continue
                        elif check_args[parameters.index(param)] == "callable":
                            assert callable(value), \
                                f"TypeError: {arg} is of type {type(arg)}, not of type callable"
                        else:
                            if not isinstance(check_args[parameters.index(param)], (list, tuple)):
                                kwarg_type = locate(check_args[parameters.index(param)])
                            else:
                                if isinstance(check_args[parameters.index(param)], list):
                                    kwarg_type = check_args[parameters.index(param)][0]
                                else:
                                    kwarg_type = tuple(check_args[parameters.index(param)])
                            assert isinstance(value, kwarg_type), \
                                 f"TypeError: {kwargs[param]} is of type {type(kwargs[param])}, not of type {kwarg_type}"

            return func(*args, **kwargs)
        return new_func

    check_args = parse_check_args(check_args)

    if callable(len(check_args) >= 1 and check_args[0]):
        return wrapper(check_args[0])
    else:
        return wrapper

