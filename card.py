#!/usr/bin/env python3
import glob, os
from yaml import load, dump
from common import Model
import config

class Card(Model):
    filename = "[[filename_without_file_extention]]"
    title = "[[title]]"
    figure = "code"#https://material.io/icons/
    description = "[[description]]"
    steps = ["Do a", "Then do b"]
    cost = "[[cost]]"
    power = "[[power]]"
    cp = "[[cp]]"
    flags = []

    def has_flag(self, flag): return flag in self.flags

def from_file(filename, in_carddir=True):#yaml syntax
    os.path.join(config.carddir, filename) if in_carddir else filename
    ret = Card()
    ret.filename = ".".join(os.path.basename(filename).split(".")[:-1])
    with open(os.path.join(config.carddir, filename) if in_carddir else filename, "r") as f:
        for key, val in load(f.read()).items():
            setattr(ret, key, val)
    return ret

def from_dir(path):
    return [from_file(i, in_carddir=False) for i in glob.glob(os.path.join(path, "*.yaml"))]
