from garethgit.procgit import ProcGit
import re

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

	def rm_remote(self, name):
		return ProcGit(
			command='remote',
			args=('rm', name),
			git_dir=self.path
		).exit_ok()

	def fetch(self, remote, progress=None):
		def escape(s):
			s = re.sub("\r\n|\r|\n", lambda m: m.group(0).replace("\r", "\\\\r").replace("\n", "\\\\n") + "\n", s)
			r = re.compile('[^-_()\[\]\{\}~`!@#$%^&*+=:;?/|\\\\\'".,<>a-zA-Z0-9\r\n \t]')
			return r.sub(lambda m: hex(ord(m.group(0))), s)

		def handle_line(line, eol):
			if not progress:
				return
			m = re.match('^remote:\s+Compressing objects:\s+(\d)%\s+\(.+\)', line)
			if m:
				progress('compressing-objects', int(m.group(1)))
				return
			m = re.match('^Receiving objects:\s+(\d+)%', line)
			if m:
				progress('receiving-objects', int(m.group(1)))
				return
			m = re.match('^Resolving deltas:\s+(\d+)%', line)
			if m:
				progress('resolving-deltas', int(m.group(1)))
				return

		output = bytearray('')
		def stderr(chunk):
			output.extend(chunk)
			while True:
				m = re.match("^([^\r\n]*)(\r\n|\r|\n)", output)
				if not m:
					break
				output[:len(m.group(0))] = ''
				handle_line(m.group(1), m.group(2))

		return ProcGit(
			command='fetch',
			args=('--verbose', '--prune', '--progress', remote),
			stderr=stderr,
			git_dir=self.path
		).exit_ok()
