import airspeed, os, html
from sanic import response
try:
    from html5print import HTMLBeautifier
except ModuleNotFoundError:
    pass
#import colorscheme#imported later instead to avoid problems with cyclic imports
import config

def readfile(path, binary=False):
    with open(path, "rb" if binary else "r") as f:
        return f.read()

#template helpers:
def escape_html(data, break_newlines=True):
    if type(data) is list:
        data = "\n".join(data)
    if type(data) is dict:
        data = "\n".join([": ".join(x) for x in data.items()])
    if data is None:
        data = ""
    if break_newlines:
        return html.escape(str(data)).replace("\n", "<br>")
    else:
        return html.escape(str(data))

def escape_url(data):
    return "ølailsf"#todo

def strip_unit(data, unit):
    if data.lower().strip().endswith(unit.lower()):
        return data.strip()[:-len(unit)].strip()
    return data.strip()

#decorators:
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

#types:
class Model:
    def __setattr__(self, name, value):
        if not hasattr(self, name):
            raise Exception(f"{self.__class__.__name__} has no attribute {name!r}")
        super(Model, self).__setattr__(name, value)
    def __repr__(self):
        return self.__class__.__name__ + "(%s)" % \
            ", ".join(f"{i}={getattr(self, i)!r}" for i in dir(self) if "_" not in (i[0], i[-1]))
    __str__ = __repr__

#fileloader:
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
            return func(*args, content, **kwargs)
        return newfunc
    return decorator

def mergeTemplate(path):
    import colorscheme

    filename = os.path.join(config.resourcedir, path)
    if config.cache:
        template = airspeed.Template(readfile(filename), filename)

    def decorator(func):
        async def newfunc(*args, **kwargs):
            if config.cache:
                tem = template
            else:
                tem = airspeed.Template(readfile(filename), filename)
                    
            objects = await func(*args, **kwargs)
            
            if type(objects) is response.HTTPResponse:
                return objects
            
            objects.update({
                "strip_unit": strip_unit,
                "escape_html": escape_html,
                "escape_url": escape_url,
                "get_colorscheme":colorscheme.get})
            
            if config.prettifyHTML:
                res = response.html(HTMLBeautifier.beautify(
                    tem.merge(objects, loader=VelocityFileLoader()),
                    indent = 4))#.replace("/>", ">")
            else:
                res = response.html(tem.merge(objects, loader=VelocityFileLoader()))

            if "write_cookies" in objects and isinstance(objects["write_cookies"], dict):
                for cookie, value in objects["write_cookies"].items():
                    res.cookies[cookie] = value

            if "delete_cookies" in objects and isinstance(objects["delete_cookies"], list):
                print(objects["delete_cookies"])
                for cookie in objects["delete_cookies"]:
                    del res.cookies[cookie]

            return res
        return newfunc
    return decorator
