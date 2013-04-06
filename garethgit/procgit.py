import re, logging
# @todo Explicitly use gevent's modules instead of the native ones
from subprocess import Popen, PIPE
from select import select
from select import error as SelectError

logger = logging.getLogger('procgit')
logger.setLevel(logging.DEBUG)

def collect_chunks(buffer):
	def handler(chunk):
		buffer.extend(chunk)
	return handler

def collect_list(list):
	def handle_line(line, EOL):
		list.append(line)
	return callback_lines(handle_line)

def callback_lines(callback):
	buffer = bytearray('')
	def handler(chunk):
		buffer.extend(chunk)
		while True:
			m = re.match("^([^\r\n]*?)(\r\n|\r|\n)", buffer, re.DOTALL)
			if not m:
				break
			callback(str(m.group(1)), str(m.group(2)))
			buffer[:len(m.group(0))] = ''
	return handler

class ProcGit():
	git_dir = None
	command = None
	args = None
	stdout = None
	stderr = None

	def __init__(self, command=None, args=(), stdout=None, stderr=None, git_dir=None):
		self.command = command
		self.args = args
		self.git_dir = git_dir
		self.stdout = stdout
		self.stderr = stderr

	def run(self):
		args = ['git', self.command]
		args.extend(self.args)
		env = {}
		if self.git_dir:
			env['GIT_DIR'] = self.git_dir
		logger.debug("Running %s" % args)
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
				chunk = p.stderr.read(1024)
				if chunk:
					# @fixme Do something with the error data
					if self.stderr:
						self.stderr(chunk)
				else:
					p.stderr.close()
					rlist.remove(p.stderr)

			if p.stdout in r:
				chunk = p.stdout.read(1024)
				if chunk:
					if self.stdout:
						self.stdout(chunk)
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

	def ok_string(self):
		output = bytearray('')
		self.stdout = collect_chunks(output)
		if self.exit_ok():
			return str(output)
		return None

	def ok_line(self):
		ret = self.ok_string()
		if ret:
			ret = ret.rstrip()
		return ret

	def return_list(self):
		output = []
		self.stdout = collect_list(output)
		self.run()
		return output
