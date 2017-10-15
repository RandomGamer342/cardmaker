import airspeed, os, html
try:
    from html5print import HTMLBeautifier
except ModuleNotfoundError:
    pass
import config

def readfile(path, binary=False):
    with open(path, "rb" if binary else "r") as f:
        return f.read()

def escape_html(data):
    return html.escape(str(data))

def escape_url(data):
    return "ølailsf"

class Model:
    def __setattr__(self, name, value):
        if not hasattr(self, name):
            raise Exception(f"{self.__class__.__name__} has no attribute {name!r}")
        super(Model, self).__setattr__(name, value)
    def __repr__(self):
        return "Card(%s)" % \
            ", ".join(f"{i}={getattr(self, i)!r}" for i in dir(self) if "_" not in i)
    __str__ = __repr__

#decorators with parameters:
def withResource(path, binary=False):
    data = readfile(os.path.join(config.resourcedir, path), binary)

    def decorator(func):
        def newfunc(*args, **kwargs):
            if not config.cache:
                with open(os.path.join(config.resourcedir, path), "rb" if binary else "r") as f:
                    content = f.read()
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
    template = airspeed.Template(readfile(os.path.join(config.resourcedir, path)))

    def decorator(func):
        def newfunc(*args, **kwargs):
            if not config.cache:
                t = airspeed.Template(readfile(os.path.join(config.resourcedir, path)))
            else:
                t = template

            class T:
                def merge(self, objects):
                    objects.update({"escape_html":escape_html, "escape_url":escape_url})
                    if config.prettifyHTML and isHTML:
                        return HTMLBeautifier.beautify(t.merge(objects), indent=4)#.replace("/>", ">")
                    else:
                        return t.merge(objects)

            if "template" in kwargs:
                kwargs["template"][os.path.basename(path)] = T()
            else:
                kwargs["template"] = {os.path.basename(path): T()}
            return func(*args, **kwargs)
        return newfunc
    return decorator
