import importlib.util
import io
import pkgutil
import sys

import importlib._bootstrap
import importlib._bootstrap
import importlib._bootstrap_external


class ModuleScanner:
    """An interruptible scanner that searches module synopses."""

    def run(self, callback, key=None, completer=None, onerror=None):
        if key: key = key.lower()
        self.quit = False
        seen = {}

        for modname in sys.builtin_module_names:
            if modname != '__main__':
                seen[modname] = 1
                if key is None:
                    callback(None, modname, '')
                else:
                    name = __import__(modname).__doc__ or ''
                    desc = name.split('\n')[0]
                    name = modname + ' - ' + desc
                    if name.lower().find(key) >= 0:
                        callback(None, modname, desc)

        for importer, modname, ispkg in pkgutil.walk_packages(onerror=onerror):
            if self.quit:
                break

            if key is None:
                callback(None, modname, '')
            else:
                try:
                    spec = pkgutil._get_spec(importer, modname)
                except SyntaxError:
                    # raised by tests for bad coding cookies or BOM
                    continue
                loader = spec.loader
                if hasattr(loader, 'get_source'):
                    try:
                        source = loader.get_source(modname)
                    except Exception:
                        if onerror:
                            onerror(modname)
                        continue
                    desc = source_synopsis(io.StringIO(source)) or ''
                    if hasattr(loader, 'get_filename'):
                        path = loader.get_filename(modname)
                    else:
                        path = None
                else:
                    try:
                        module = importlib._bootstrap._load(spec)
                    except ImportError:
                        if onerror:
                            onerror(modname)
                        continue
                    desc = module.__doc__.splitlines()[0] if module.__doc__ else ''
                    path = getattr(module, '__file__', None)
                name = modname + ' - ' + desc
                if name.lower().find(key) >= 0:
                    callback(path, modname, desc)

        if completer:
            completer()
