import glob, os
import config
from common import memoize, listify_output

@listify_output
def list_all():
    for i in glob.glob(os.path.join(config.svgdir, "*.svg")):
        yield os.path.basename(i)[:-4]
        
        
@memoize
def get(name):
    with open(os.path.join(config.svgdir, f"{name}.svg"), "r") as f:
        return f.read()

def store(name, data):
    with open(os.path.join(config.svgdir, f"{name}.svg"), "wb" if type(data) is bytes else "w") as f:
        return f.write(data)
