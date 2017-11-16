import glob, os
import config
from common import memoize, listify_output

@listify_output
def list_all(collection = None):
    if collection:
        for i in glob.glob(os.path.join(config.svgdir, collection, "*.svg")):
            yield os.path.join(collection, os.path.basename(i)[:-4])
    else:
        for i in glob.glob(os.path.join(config.svgdir, "*.svg")):
            yield os.path.basename(i)[:-4]

@listify_output
def list_collections():
    for i in glob.glob(os.path.join(config.svgdir, "*")):
        if not i.endswith(".svg"):
            yield os.path.basename(i)


@memoize
def get(name, color=None):
    with open(os.path.join(config.svgdir, f"{name}.svg"), "r") as f:
        if not color:
            return f.read()
        return (f.read() #EW!
            .replace("style=\"fill:#", f"style=\"fill:#{color};")
            .replace("style='fill:#", f"style='fill:#{color};")
            .replace("fill=\"#", f"fill=\"#{color}\" asdasd=\"")
            .replace("fill='#", f"fill='#{color}' asdasd='")
            .replace("<svg", f"<svg fill=\"#{color}\"")
            )
        

def store(name, data):
    with open(os.path.join(config.svgdir, f"{name}.svg"), "wb" if type(data) is bytes else "w") as f:
        return f.write(data)
