from functools import wraps
from pydoc import locate
from functools import partial
import inspect

class TypeCheckerIgnore:
    pass

class TypeCheckerUnset:
    pass

class TypeCheckError(Exception):
    """Raise when type-checker cannot check the arguments."""
    pass

def typecheck(*check_args, check_return_type=TypeCheckerUnset, **check_kwargs):
    """
        Checks that arguments passed to function
        is of the type passed to the type checker.
    """

    def error(err_type, err_msg):
        raise err_type(err_msg)

    t_error = partial(error, TypeError)
    tc_error = partial(error, TypeCheckError)

    IGNORE = TypeCheckerIgnore()
    UNSET = TypeCheckerUnset()

    def get_fn_param(fn):
        """ Returns a list of parameters and a list of
        default values belonging to fn """

        # Get parameter list
        params = [param.strip() for param in str(inspect.signature(fn)).replace("(", "").replace(")", "").split(",")]

        # Remove type hints
        params = [param.split(':')[0] for param in params]

        # Store possible default values in separate list
        defaults = [param.split('=')[0] for param in params if len(param.split('=')) > 1 ]

        # Remove default values
        params = [param.split('=')[0] for param in params]

        return params, defaults

    def get_fn_name(fn):
        """ Returns a string of the functions name """
        return str(fn).split()[1].split(".")[-1]

    def pass_filter(tup):
        """ Filters out check tuples that contains pass as an option """
        return tup if "pass" not in tup else IGNORE

    def setup_param_dict(fn, args, kwargs):
        """ Creates and returns a dictionary of the types
            that is to be checked, formatted as:
                { parameter_name : expected_type }
        """
        params, _ = get_fn_param(fn)

        # Make a params dict with all values being UNSET
        params = { kw_param : UNSET for kw_param in params }

        # Go through and add all args
        for param, arg in zip(params, args):
            params[param] = parse_arg(arg)

        # Go through and add all kwargs (if collision throw error)
        for param, check_type in kwargs.items():
            try:
                if params[param] is not UNSET:
                    raise tc_error(f"The kwarg '{param}' is already set by arg")
                params[param] = parse_arg(check_type)
            except KeyError:
                raise tc_error(f"The given kwarg '{param}' is not a parameter of function '{fn}'")

        # Replace all UNSET with IGNORE
        for param in params:
            if params[param] == UNSET:
                params[param] = IGNORE
        return params

    def unify_values(fn, args, kwargs):
        """ Creates and returns a unified dictionary of given
            arguments and keyword arguments, formatted as:
                { parameter_name : given_value }
        """
        params, defaults = get_fn_param(fn)
        params = { param : UNSET for param in params }

        # Add argument values
        for param, arg in zip(params, args):
            params[param] = arg

        # Add kwarg values
        for param in kwargs:
            params[param] = kwargs[param]

        # Check for UNSET, if UNSET and in defaults
        # set to IGNORE
        for param, value in params.items():
            if value != UNSET:
                continue

            if param not in defaults:
                tc_error(f"The parameter '{param}' got no value")

            params[param] = IGNORE

        return params

    def parse_arg(parse_arg):
        """ Convert input to manageable type

            If no types given, leave as it is;
            If class insert into sub-list;
            If function set to callable check;
            If string 'pass' set to IGNORE
            If tuple leave it
            Else send primitive type as string;
        """
        return      parse_arg if str(parse_arg).startswith("<function") else \
                    IGNORE if parse_arg == "pass" else \
                    pass_filter(parse_arg) if isinstance(parse_arg, tuple) else \
                    [parse_arg] if str(parse_arg).startswith("<class '__main__.") else \
                    'callable' if str(parse_arg) == '<built-in function callable>' else \
                    str(parse_arg).replace("<class '", "").replace("'>", "")


    def wrapper(func):
        @wraps(func)
        def typechecking(*args, **kwargs):
            """ Performs the type checking """

            check_types = setup_param_dict(func, check_args, check_kwargs)
            values = unify_values(func, args, kwargs)
            # check_types and values are now dictionaries containing the
            # same keys, now just check that the values are correct.

            for param in check_types:
                if check_types[param] == IGNORE or values[param] == IGNORE:
                    continue
                elif check_types[param] == 'callable':
                    if not callable(values[param]):
                        t_error(f"The value '{values[param]}' sent to parameter '{param}' "\
                                f"of function '{get_fn_name(func)}' is of type {type(values[param])}, expected callable")
                else:
                     if not isinstance(check_types[param], (list, tuple)): # If not class or tuple of optional types
                         arg_type = locate(check_types[param]) # Convert check type string to checkable type
                         if arg_type is None:
                             arg_type = type(None)
                     else:
                         if isinstance(check_types[param], list): # If class instance
                             arg_type = check_types[param][0]
                         else:
                             arg_type = tuple(check_types[param]) # If optional types

                     if not isinstance(values[param], arg_type):
                         t_error(f"The value '{values[param]}' sent to parameter '{param}' "\
                                 f"of function '{get_fn_name(func)}' is of type {type(values[param])}, expected type {arg_type}")

            result = func(*args, **kwargs)

            if check_return_type is not TypeCheckerUnset and not isinstance(result, check_return_type):
                t_error(f"The value '{result}' returned from function '{get_fn_name(func)}' is of type {type(result)}, "\
                f"expected type {check_return_type}")
            else:
                return result

        return typechecking

    def nocheckwrapper(func):
        """ If no given checks, just run func and return value """
        @wraps(func)
        def some_func(*args, **kwargs):
            return func(*args, **kwargs)
        return some_func

    if len(check_args) == 1 and callable(parse_arg(check_args[0])):
        return nocheckwrapper(check_args[0])
    else:
        return wrapper

