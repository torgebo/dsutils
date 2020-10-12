from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader


def get_module(script_name: str):
    spec = spec_from_loader(
        script_name, SourceFileLoader(script_name, script_name),
    )
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
