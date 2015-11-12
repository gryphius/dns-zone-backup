class ProviderBase(object):
    def __init__(self):
        self.configsection=None
        self.configvars={}
        self.helpstrings={}

    def lint(self):
        pass

    def get_zones(self):
        pass

    def get_records(self,zonename):
        pass

    def prepare(self):
        pass

    def cleanup(self):
        pass

