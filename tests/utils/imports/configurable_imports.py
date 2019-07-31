from unittest.mock import MagicMock

___import__real = None
_modules_to_raise_importerrors = []
_modules_to_return_magicmocks = []

def configure_imports(__import__real, 
                      modules_to_raise_importerrors = [],
                      modules_to_return_magicmocks = []):
    """Call this before monkeypatching builtins.__import__. This function
    needs the real builtins.__import__ function passed in as the first arg,
    with the second argument being a list of strings of module names that 
    you want to configure to raise `ImportError`s on `import foo`.
    """
    global ___import__real
    global _modules_to_raise_importerrors
    global _modules_to_return_magicmocks

    ___import__real = __import__real
    _modules_to_raise_importerrors = modules_to_raise_importerrors
    _modules_to_returns_magicmocks = modules_to_return_magicmocks

def __import__custom(*args, **kwargs):
    """The actual function that you monkeypatch to builtins.__import__.
    MAKE SURE YOU CALL `configure_imports`()` BEFORE MONKEYPATCHING
    """
    if ___import__real == None:
        raise Exception("You must call `configure_imports()` and pass in the "\
                        "the real builtins.__import__ before monkeypatching "\
                        "this __import__custom() func to builtins.__import__")
    name = args[0]
    if any([name.split(".")[0] == mod \
               for mod in _modules_to_raise_importerrors]):
        raise ImportError(f"module {name} monkeypatched to raise ImportError")
    elif any([name.split(".")[0] == mod \
               for mod in _modules_to_return_magicmocks]):
        return MagicMock()
    else:
        return ___import__real(*args, **kwargs)
