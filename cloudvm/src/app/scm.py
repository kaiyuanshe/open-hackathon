__author__ = 'junbo'

from gittle import Gittle

class SCM(object):
    def __init__(self, provider):
        if provider=="git":
            self.provider = Git()

        self.provider = Git()

    def clone(self, args):
        self.provider.clone(args)

class SCMProvider(object):
    def clone(self, args):
        pass

    def submit(self, args):
        pass

class Git(SCMProvider):
    def clone(self, args):
        Gittle.clone(args["repo_url"], args["local_repo_path"])
