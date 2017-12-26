import glob, os
from common import Model, wrap_output
import config

class ColorScheme(Model):
    filename = ""
    border = "4a4a4a"
    card_bg = "4a4a4a"
    main_bg = "ddd"
    main = "000"
    header = "ddd"
    header_bg = "111"
    figure = "aaa"
    figure_bg = "2a2a2a"
    costbar = "eee"
    costbar_bg = "111"

def get(filename):
    if not filename:
        return ColorScheme()
    with open(os.path.join(config.colordir, f"{filename}.yaml"), "r") as f:
        return from_yaml(f.read(), filename=filename)
def store(colorscheme):
    assert colorscheme.filename, "no filename set"
    
    with open(os.path.join(config.colordir, f"{filename}.yaml"), "w") as f:
        f.write(to_yaml(colorscheme))
def delete(filename):
    if type(filename) is ColorScheme:
        assert filename.filename, "no filename set"
        filename = filename.filename
    os.remove(os.path.join(config.colordir, f"{filename}.yaml"))

@wrap_output(list)
def list_all():
    yield ColorScheme()
    for i in glob.glob(os.path.join(config.colordir, "*.yaml")):
        yield get(os.path.basename(i)[:-5])

def from_yaml(data, filename="from_yaml"):
    colorscheme = ColorScheme()
    colorscheme.filename = filename
    for key, val in load(data).items():
        setattr(colorscheme, key, val)
    return colorscheme
def to_yaml(colorscheme):
    out = {}
    for key in dir(colorscheme):
        if "_" not in key[0] and key != "filename":
            val = getattr(colorscheme, key)
            if (val or val==0) and val != getattr(ColorScheme, key):
                out[key] = val
    return dump(out, default_flow_style=False)
def from_form(form):#sanic's request.form
    colorscheme = ColorScheme()
    for key, val in form.items():
        if not val[0]: continue
        setattr(colorscheme, key, val[0].strip())
    return colorscheme
