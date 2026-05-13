import sys


class OptionalPyArrowBlocker:
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "pyarrow" or fullname.startswith("pyarrow."):
            raise ModuleNotFoundError("Optional pyarrow package is disabled for this app.")
        return None


def disable_optional_pyarrow():
    if not any(isinstance(finder, OptionalPyArrowBlocker) for finder in sys.meta_path):
        sys.meta_path.insert(0, OptionalPyArrowBlocker())
