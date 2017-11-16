import airspeed, os, html
try:
    from html5print import HTMLBeautifier
except ModuleNotfoundError:
    pass
import config

def readfile(path, binary=False):
    with open(path, "rb" if binary else "r") as f:
        return f.read()

def escape_html(data, break_newlines=True):
    if type(data) is list:
        data = "\n".join(data)
    if data is None:
        data = ""
    if break_newlines:
        return html.escape(str(data)).replace("\n", "<br>")
    else:
        return html.escape(str(data))

def escape_url(data):
    return "ølailsf"#todo

def memoize(func):#a decorator
    class Memoizer(dict):
        def getter(self, *args, **kwargs):
            return self[(args, frozenset(kwargs.items()))]
        def __missing__(self, key):
            ret = self[key] = func(*key[0], **dict(key[1]))
            return ret
    return Memoizer().getter

def memoize_singlearg(func):#a decorator
    class Memoizer(dict):
        def __missing__(self, key):
            ret = self[key] = func(key)
            return ret
    return Memoizer().__getitem__

def wrap_output(type):#decorator with parameters
    def decorator(func):#decorator
        def new_func(*args, **kwargs):
            return type(func(*args, **kwargs))
        return new_func
    return decorator

def call(func):#decorator
    return func()

class Model:
    def __setattr__(self, name, value):
        if not hasattr(self, name):
            raise Exception(f"{self.__class__.__name__} has no attribute {name!r}")
        super(Model, self).__setattr__(name, value)
    def __repr__(self):
        return "Card(%s)" % \
            ", ".join(f"{i}={getattr(self, i)!r}" for i in dir(self) if "_" not in i)
    __str__ = __repr__

class VelocityFileLoader:
    _cache = {}#static cache, shared between instances
    def get_file(self, filename):
        file = readfile(filename)
        if filename[-4:] == ".svg":
            pass#file = file.replace("fill:#", "")#a nasty hack
        return file
    def load_text(self, name):
        if name[-4:] == ".svg":
            filename = os.path.join(config.svgdir, name)
        else:
            filename = os.path.join(config.resourcedir, name)
        if config.cache:
            if filename not in self.memory:
                self._cache[filename] = self.get_file(filename)
            return self._cache[filename]
        return self.get_file(filename)

#decorators with parameters:
def withResource(path, binary=False):
    if config.cache:
        data = readfile(os.path.join(config.resourcedir, path), binary)

    def decorator(func):
        def newfunc(*args, **kwargs):
            if not config.cache:
                content = readfile(os.path.join(config.resourcedir, path), binary)
            else:
                content = data
            if "file" in kwargs:
                kwargs["file"][os.path.basename(path)] = content
            else:
                kwargs["file"] = {os.path.basename(path): content}
            return func(*args, **kwargs)
        return newfunc
    return decorator

def withTemplate(path, isHTML=True):
    filename = os.path.join(config.resourcedir, path)
    if config.cache:
        template = airspeed.Template(readfile(filename), filename)

    def decorator(func):
        def newfunc(*args, **kwargs):
            if not config.cache:
                t = airspeed.Template(readfile(filename), filename)
            else:
                t = template

            class T:
                def merge(self, objects):
                    objects.update({"escape_html":escape_html, "escape_url":escape_url})
                    if config.prettifyHTML and isHTML:
                        return HTMLBeautifier.beautify(
                            t.merge(objects, loader=VelocityFileLoader()),
                            indent=4)#.replace("/>", ">")
                    else:
                        return t.merge(objects, loader=VelocityFileLoader())

            if "template" in kwargs:
                kwargs["template"][os.path.basename(path)] = T()
            else:
                kwargs["template"] = {os.path.basename(path): T()}
            return func(*args, **kwargs)
        return newfunc
    return decorator
