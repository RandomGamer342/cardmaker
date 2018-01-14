#!/usr/bin/env python3
import glob, os
from yaml import load, dump
from common import Model
import config
from figure import Figure

class Card(Model):
    filename = ""#filename without extentions
    title = "title"
    figure = ["code"]
    figure_source = "material-icons"
    figure_parsed = []
        #material-icons = https://material.io/icons/
        #mdi            = https://materialdesignicons.com/
        #fa             = http://fontawesome.io/icons/
        #svg            = the svgs/ folder
    description = ""
    steps = []
    effects = []
    cost = ""
    stats = {}
    power = None
    cp = None
    gp = None#gold
    flags = []
    notes = ""#not shown, but used to keep track of things
    copies_owned = 1
    tags = [""]
    
    def has_flag(self, flag):
        return flag.lower() in map(lambda x: x.lower(), self.flags)

    def has_tag(self, tag):
        return tag.lower() in map(lambda x: x.lower(), self.tags)

    def has_tags(self, tags):
        for tag in tags:
            if not self.has_tag(tag):
                return False
        return True

    def get_sorted_tags(self):
        return sorted(self.tags) if self.tags else ["\0"]


#todo: make the relevant ones into coroutines:

def from_file(filename, in_carddir=True):#yaml syntax
    if filename[-5:] != ".yaml":
        filename += ".yaml"
    name = ".".join(os.path.basename(filename).split(".")[:-1])
    with open(os.path.join(config.carddir, filename) if in_carddir else filename, "r") as f:
        return from_yaml(f.read(), name)

def to_file(card, in_carddir=True):
    assert card.filename, "no filename set"
    filename = card.filename+".yaml"
    
    with open(os.path.join(config.carddir, filename) if in_carddir else filename, "w") as f:
        f.write(to_yaml(card))

def del_file(card, in_carddir=True):
    assert card.filename, "no filename set"
    filename = card.filename+".yaml"
    os.remove(os.path.join(config.carddir, filename) if in_carddir else filename)

def from_yaml(data, filename="from_yaml"):
    card = Card()
    card.filename = filename
    for key, val in load(data).items():
        if key == "tag":
            setattr(card, "tags", [val])
            continue
        if type(getattr(Card, key)) is int:
            val = int(val)
        setattr(card, key, val)
    setattr(card, "figure_parsed", [Figure(line, getattr(card, "figure_source")) for line in getattr(card, "figure")])
    return card

def to_yaml(card):
    out = {}
    for key in dir(card):
        if "_" not in key[0] and key not in ("filename", "has_flag", "has_tag", "has_tags", "figure_parsed", "get_sorted_tags"):
            val = getattr(card, key)
            if (val or val==0) and val != getattr(Card, key):
                if type(getattr(Card, key)) is int:
                    val = int(val)
                out[key] = val
    return dump(out, default_flow_style=False)

def from_dir(path):
    return [from_file(i, in_carddir=False) for i in glob.glob(os.path.join(path, "*.yaml"))]

def from_form(form):#sanic's request.form
    card = Card()
    for key, val in form.items():
        print(key, ",", val)
        if not val[0]: continue
        if key in ("save", "delete"): continue
        if type(getattr(Card, key)) in (tuple, list):
            if len(val) == 1 and "\n" in val[0]:
                val = val[0].strip().replace("\r\n", "\n").split("\n")
                #val = [i for i in val if i]
            setattr(card, key, val)
        elif type(getattr(Card, key)) is dict:
            if len(val) == 1 and "\n" in val[0]:
                val = val[0].strip().replace("\r\n", "\n").split("\n")
            val = dict([[y.strip() for y in x.split(":")] for x in val])
            setattr(card, key, val)
        else:
            setattr(card, key, val[0].strip().replace("\r\n", "\n"))
    setattr(card, "figure_parsed", [Figure(line, getattr(card, "figure_source")) for line in getattr(card, "figure")])
    return card

def is_filename_vacant(filename, in_carddir=True):
    if in_carddir:
        filename = os.path.join(config.carddir, filename)
    if filename[-5:] != ".yaml":
        filename += ".yaml"
    return not os.path.exists(filename)

def get_vacant_filename():
    i = 1
    while 1:
        if is_filename_vacant("card-%s" % str(i).zfill(4)):
            return "card-%s" % str(i).zfill(4)
        i += 1

class open_file:#contextmanager
    def __init__(self, filename):
        self.filename = filename
    def __enter__(self):
        self.card = from_file(self.filename)
        return self.card
    def __exit__(self, *args):
        to_file(self.card)