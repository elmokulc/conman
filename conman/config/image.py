from __future__ import annotations
from conman.commands.install import Container


class Image(Container):
    def __init__(self, name, tag, **kwargs):
        self.name = name
        self.tag = tag
        super().__init__(**kwargs)
        
    def check(self):
        print("Check image")