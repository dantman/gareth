from garethgit.procgit import ProcGit

class GarethGit():
	path = None
	def __init__(self, path):
		self.path = path

	def initialize(self):
		return ProcGit(
			command='init',
			args=('--bare', '--', self.path)
		).exit_ok()

	def add_remote(self, name, url):
		return ProcGit(
			command='remote',
			args=('add', name, url),
			git_dir=self.path
		).exit_ok()
