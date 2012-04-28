from garethgit.procgit import ProcGit
import os.path
import re

class State():
	pass

class GarethGitRef():
	def __init__(self, git, ref, name=None):
		self.git = git
		self.ref = ref
		if not name:
			name = ref
		self.name = name

	def __unicode__(self):
		return self.name

	@property
	def symbolic(self):
		ref = self.git.get_symbolic_ref(self.ref)
		if ref:
			return self.git.ref_obj(ref)
		return None

	@property
	def content(self):
		with open(self.git.rel_path(self.ref), 'r') as f:
			return f.read().rstrip()
		return None

	@property
	def sha1(self):
		ref = self
		while ref.symbolic:
			ref = ref.symbolic
		return ref.content

class GarethGitRemoteBranch(GarethGitRef):
	def __init__(self, git, remote, branch, name=None):
		if not name:
			name = branch
		GarethGitRef.__init__(self, git, "refs/remotes/%s/%s" % (remote, branch), name)

	@property
	def unreviewed(self):
		return self.git.unmerged_commits(self.ref)

class GarethGitCommit():
	def __init__(self, git, sha1):
		self.git = git
		self.sha1 = sha1

	def __unicode__(self):
		return self.sha1

class GarethGit():
	path = None
	def __init__(self, path):
		self.path = path

	def initialize(self):
		return ProcGit(
			command='init',
			args=('--bare', '--', self.path)
		).exit_ok()

	def rel_path(self, name):
		return os.path.join(self.path, name)

	def ref_obj(self, ref, name=None):
		return GarethGitRef(self, ref, name)

	def commit_obj(self, sha1):
		return GarethGitCommit(self, sha1)

	def remotebranch_obj(self, remote, branch, name=None):
		return GarethGitRemoteBranch(self, remote, branch, name)

	def get_symbolic_ref(self, ref):
		return ProcGit(
			command='symbolic-ref',
			args=('-q', ref),
			git_dir=self.path
		).ok_line()

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

	def remote_branches(self, name):
		st = State()
		st.branches = []
		st.section = None
		def handle_line(line, eol):
			line = re.sub('^[* ] ', '', line)
			m = re.match('^( *)(.*)$', line)
			if not m:
				return
			spaces = m.group(1)
			line = m.group(2)
			if len(spaces) == 0:
				if re.match('^Remote branches:', line):
					st.section = 'branches'
				else:
					st.section = None
			elif st.section == 'branches':
				st.branches.append(line)

		output = bytearray('')
		def stdout(chunk):
			output.extend(chunk)
			while True:
				m = re.match("^([^\r\n]*?)(\r\n|\r|\n)", output)
				if not m:
					break
				# Handle a line (Must be first, if you shift data first this will break)
				handle_line(str(m.group(1)), str(m.group(2)))
				# Shift out the line that we handled
				output[:len(m.group(0))] = ''

		ok = ProcGit(
			command='remote',
			args=('show', '-n', name),
			stdout=stdout,
			git_dir=self.path
		).exit_ok()
		if not ok:
			return None
		return [self.remotebranch_obj(name, branch) for branch in st.branches]

	def fetch(self, remote, progress=None):
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
				m = re.match("^([^\r\n]*?)(\r\n|\r|\n)", output)
				if not m:
					break
				handle_line(m.group(1), m.group(2))
				output[:len(m.group(0))] = ''

		return ProcGit(
			command='fetch',
			args=('--verbose', '--prune', '--progress', remote),
			stderr=stderr,
			git_dir=self.path
		).exit_ok()

	def unmerged_commits(self, ref=None, remote=None, branch=None):
		if not ref:
			ref = "refs/remotes/%s/%s" % (remote, branch)
		revs = ProcGit(
			command='rev-list',
			args=(ref, '--not', '--glob', 'refs/heads/*', '--glob', 'refs/review-heads/*'),
			git_dir=self.path
		).return_list()
		return [self.commit_obj(rev) for rev in revs]
