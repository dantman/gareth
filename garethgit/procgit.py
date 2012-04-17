from subprocess import Popen, PIPE
from select import select
from select import error as SelectError

class ProcGit():
	git_dir = None
	command = None
	args = None

	def __init__(self, command=None, args=[], git_dir=None):
		self.command = command
		self.args = args
		self.git_dir = git_dir

	def run(self):
		args = ['git', self.command]
		args.extend(self.args)
		env = {}
		if self.git_dir:
			env['GIT_DIR'] = self.git_dir
		p = Popen(args, stdout=PIPE, stderr=PIPE, cwd=self.git_dir, env=env)

		rlist = [p.stderr, p.stdout]
		wlist = []
		xlist = []


		while len(rlist) > 0 or len(wlist) > 0:
			try:
				r, w, x = select(rlist, wlist, xlist)
			except SelectError, e:
				break

			if p.stderr in r:
				chunk = p.stderr.read()
				if chunk:
					# @fixme Do something with the error data
					pass
				else:
					p.stderr.close()
					rlist.remove(p.stderr)

			if p.stdout in r:
				chunk = p.stdout.read()
				if chunk:
					# @fixme Do something with the error data
					pass
				else:
					p.stdout.close()
					rlist.remove(p.stdout)

			p.wait()
			self._exit_code = p.returncode

	def exit_code(self):
		self.run()
		return self._exit_code

	def exit_ok(self):
		return self.exit_code() == 0
