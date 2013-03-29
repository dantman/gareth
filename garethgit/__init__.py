from garethgit.procgit import ProcGit, callback_lines
from garethgit import syntaxdiff as diff
from hashlib import md5
from urllib import urlencode
from datetime import datetime
import pytz
import os.path
import re

class State(object):
	pass

class GitHash(object):
	def __init__(self, sha1):
		self.sha1 = sha1

	@property
	def abbrhash(self):
		return self.sha1[0:8]

class GarethGitUser(object):
	def __init__(self, name, email):
		self.name = name
		self.email = email

	@property
	def avatar(self):
		return "http://www.gravatar.com/avatar/%s?%s" % (md5(self.email.lower()).hexdigest(), urlencode({'s': 40}))

	@property
	def miniavatar(self):
		return "http://www.gravatar.com/avatar/%s?%s" % (md5(self.email.lower()).hexdigest(), urlencode({'s': 24}))

	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return "%s <%s>" % (self.name, self.email)

class GitRef(object):
	def __init__(self, git, ref, name=None):
		self.git = git
		self.ref = ref
		if not name:
			name = ref
		self.name = name

	def __str__(self):
		return self.__unicode__()
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

class GarethGitRemoteBranch(GitRef):
	def __init__(self, git, remote, branch, name=None):
		if not name:
			name = branch
		GitRef.__init__(self, git, "refs/remotes/%s/%s" % (remote, branch), name)

	@property
	def unreviewed(self):
		return self.git.unmerged_commits(self.ref)

class GarethGitDiffChange(object):
	# types = {
	# 	'A': 'add',
	# 	'C': 'copy',
	# 	'D': 'delete',
	# 	'M': 'modify',
	# 	'R': 'rename',
	# 	'T': 'type',
	# }
	def __init__(self, diff, change):
		self.diff = diff
		self._change = change

	@property
	def type(self):
		return self._change['change_type']
		# if self.change_type in self.types:
		# 	return self.types[self.change_type]
		# return self.change_type

	# @property
	# def change_type(self):
	# 	return self._change['change_type']

	@property
	def total_lines(self):
		return int(self._change['add_lines']) + int(self._change['del_lines'])

	@property
	def diffstat(self, statlength=5):
		total = float(self.diff.max_total_lines)
		if total:
			added = round((float(self._change['add_lines']) / total) * statlength)
			deleted = round((float(self._change['del_lines']) / total) * statlength)
		else:
			added = 0
			deleted = 0
		leftover = statlength - added - deleted
		return tuple(('+' * int(added)) + ('-' * int(deleted)) + (' ' * int(leftover)))

	@property
	def old_path(self):
		return self._change['old_path']

	@property
	def new_path(self):
		return self._change['new_path']

	@property
	def old_hash(self):
		return GitHash(self._change['old_hash'])

	@property
	def new_hash(self):
		return GitHash(self._change['new_hash'])

	@property
	def htmldiff(self):
		try:
			old = self.diff.git.cat_blob(self.old_hash.sha1)
			new = self.diff.git.cat_blob(self.new_hash.sha1)
			return diff.render(
				old_path=self.old_path,
				old_blob=old,
				new_path=self.new_path,
				new_blob=new
			)
		except Exception, e:
			import traceback
			traceback.print_exc()
			raise

	@property
	def path(self):
		return self._change['path']

class GarethGitDiff(object):
	def __init__(self, git, changes):
		self.git = git
		self._changes = changes

	@property
	def max_total_lines(self):
		return max((change.total_lines for change in self.changes))

	@property
	def changes(self):
		return (GarethGitDiffChange(self, v) for v in self._changes.itervalues())

class GitMode(object):
	def __init__(self, mode):
		if isinstance(mode, str):
			mode = int(mode, 8)
		self.mode = mode

	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return "%o" % self.mode

class GitCommit(GitHash):
	def __init__(self, git, sha1):
		self.git = git
		self.sha1 = sha1
		self._c = None

	def cat_data(self, name, default=None):
		if not self._c:
			self._c = self.git.cat_commit(self.sha1)
		if name in self._c:
			return self._c[name]
		return default

	@property
	def author(self):
		return self.cat_data('author')

	@property
	def committer(self):
		return self.cat_data('committer')

	@property
	def authored_at(self):
		return self.cat_data('authored_at')

	@property
	def committed_at(self):
		return self.cat_data('committed_at')

	@property
	def message(self):
		return self.cat_data('message')

	@property
	def parents(self):
		return map(lambda sha1: GitHash(sha1), self.cat_data('parents', []))

	@property
	def parent(self):
		return self.parents[0]

	@property
	def title(self):
		return self.message.split("\n")[0]

	@property
	def messagecont(self):
		return "\n".join(self.message.split("\n")[1:]).lstrip("\n")

	@property
	def diff(self):
		return self.git.complete_diff(self.sha1)

	def __unicode__(self):
		return self.sha1

class GarethGit(object):
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
		return GitRef(self, ref, name)

	def commit_obj(self, sha1):
		return GitCommit(self, sha1)

	def remotebranch_obj(self, remote, branch, name=None):
		return GarethGitRemoteBranch(self, remote, branch, name)

	def get_symbolic_ref(self, ref):
		return ProcGit(
			command='symbolic-ref',
			args=('-q', ref),
			git_dir=self.path
		).ok_line()

	def cat_blob(self, sha1):
		return ProcGit(
			command='cat-file',
			args=('blob', sha1),
			git_dir=self.path
		).ok_string()

	def cat_commit(self, sha1):
		st = State()
		st.inmessage = False
		st.message = bytearray('')
		st.parents = []
		def stdoutline(line, EOL):
			if st.inmessage:
				st.message.extend("%s\n" % line)
			elif len(line) == 0:
				# Blank line indicates a switch to commit message
				st.inmessage = True
			else:
				m = re.match('^(tree|parent)\s+([0-9a-fA-F]{40})$', line)
				if m:
					if m.group(1) == 'tree':
						st.tree = m.group(2)
					elif m.group(1) == 'parent':
						st.parents.append(m.group(2))
					else:
						raise Exception("%s is not valid" % m.group(1))
					return
				m = re.match('^(author|committer)\s+(.+)\s+<(.+?)>\s+(\d+)\s+([-+]?\d+)$', line)
				if m:
					user = GarethGitUser(name=m.group(2), email=m.group(3))
					time = datetime.fromtimestamp(int(m.group(4)))
					if m.group(1) == 'author':
						st.author = user
						st.authored_at = time
					elif m.group(1) == 'committer':
						st.committer = user
						st.committed_at = time
					else:
						raise Exception("Unknown user type '%s'" % m.group(1))
					return
				raise Exception("Unknown line '%s' in git commit." % line)

		ret = ProcGit(
			command='cat-file',
			args=('commit', sha1),
			stdout=callback_lines(stdoutline),
			git_dir=self.path
		).exit_ok()
		if not ret:
			return None

		commit = {}
		commit['message'] = str(st.message)
		if st.tree:
			commit['tree'] = st.tree
		if st.parents:
			commit['parents'] = st.parents
		if st.author:
			commit['author'] = st.author
		if st.authored_at:
			commit['authored_at'] = st.authored_at
		if st.committer:
			commit['committer'] = st.committer
		if st.committed_at:
			commit['committed_at'] = st.committed_at

		return commit

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
			args=('--verbose', '--prune', '--no-tags', '--progress', remote),
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

	def complete_diff(self, commit):
		st = State()
		st.first = True
		st.diffbody = False
		st.change = {}
		st.diff = {}

		output = bytearray('')
		def stdout(chunk):
			output.extend(chunk)
			while True:
				if not st.diffbody:
					# Header; Raw (changed list) + Stat (lines changed)

					if st.first:
						m = re.match('^[0-9a-z]{40}\0', output)
						if m:
							output[:len(m.group(0))] = ''
							st.first = False
							continue

					# Handle copy and rename changes
					m = re.match('^:(\d+) (\d+) ([0-9a-z]+(?:\.{3})?) ([0-9a-z]+(?:\.{3})?) ([CR])(\d+)\0(.*?)\0(.*?)\0', output, re.DOTALL)
					if m:
						output[:len(m.group(0))] = ''
						raise NotImplementedError("Copy/Rename handling not implemented.")
						st.first = False
						continue

					# Handle changes
					m = re.match('^:(\d+) (\d+) ([0-9a-z]+(?:\.{3})?) ([0-9a-z]+(?:\.{3})?) ([A-Z])\0(.*?)\0', output, re.DOTALL)
					if m:
						if str(m.group(5)) not in "ADMTUX":
							raise Exception("Invalid change type %s" % m.group(5))
						path = str(m.group(6))
						st.change[path] = {
							'old_mode': GitMode(str(m.group(1))),
							'new_mode': GitMode(str(m.group(2))),
							'old_hash': str(m.group(3)),
							'new_hash': str(m.group(4)),
							'add_lines': 0,
							'del_lines': 0,
							'change_type': str(m.group(5)),
							'old_path': path,
							'new_path': path,
							'path': path,
						}
						output[:len(m.group(0))] = ''
						st.first = False
						continue

					# Handle number of lines modified in renames/coppies
					m = re.match('^(\d+|-)\t(\d+|-)\t\0(.*?)\0(.*?)\0', output, re.DOTALL)
					if m:
						output[:len(m.group(0))] = ''
						raise NotImplementedError("Copy/Rename handling not implemented.")
						st.first = False
						continue

					# Handle number of lines modified in changes
					m = re.match('^(\d+|-)\t(\d+|-)\t(.*?)\0', output, re.DOTALL)
					if m:
						path = str(m.group(3))
						if m.group(1) != '-':
							st.change[path]['add_lines'] = int(m.group(1))
						if m.group(2) != '-':
							st.change[path]['del_lines'] = int(m.group(2))
						output[:len(m.group(0))] = ''
						st.first = False
						continue

					# A finial NUL indicates the end of the header
					m = re.match('^\0', output)
					if m:
						st.diffbody = True
						output[:len(m.group(0))] = ''
						st.first = False
						continue

					if re.match('\n', output):
						raise Exception("Unknown diff output found: '%s'." % output[:64])

					# We may not have enough data, wait for the next chunk
					break
				else:
					# Body of the diff

					m = re.match('^-{3} (.*?)\n\+{3} (.*?)\n', output)
					if m:
						old_path = str(m.group(1))
						new_path = str(m.group(2))

						# Copy the path if one is /dev/null
						if old_path == "/dev/null":
							old_path = new_path
						elif new_path == "/dev/null":
							new_path = old_path
						if old_path == new_path:
							path = old_path
							st.cur_diff = {
								'old_path': old_path,
								'new_path': new_path,
								'path': path,
								'chunks': [],
							}
							st.diff[path] = st.cur_diff
							st.cur_chunk = None
						else:
							raise NotImplementedError("Copy/Rename handling not implemented: %s -> %s" % (old_path, new_path))
						output[:len(m.group(0))] = ''
						continue

					m = re.match('^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?: (.*?))?\n', output)
					if m:
						if not st.cur_diff:
							raise Exception("@@ line found outside of a diff: %s " % m.group(0))
						st.cur_chunk = {
							'heading': str(m.group(5)),
							'lines': [],
							'cur_old_linenum': int(m.group(1)),
							'cur_new_linenum': int(m.group(3)),
						}
						st.cur_diff['chunks'].append(st.cur_chunk)
						output[:len(m.group(0))] = ''
						continue

					m = re.match('^([-+ ])(.*?)\n', output)
					if m:
						if not st.cur_chunk:
							raise Exception("Diff line found outside of a chunk: %s " % m.group(0))
						t = str(m.group(1))
						old_line = None
						new_line = None
						if t == '-':
							old_line = st.cur_chunk['cur_old_linenum']
							st.cur_chunk['cur_old_linenum'] += 1
						elif t == '+':
							new_line = st.cur_chunk['cur_new_linenum']
							st.cur_chunk['cur_new_linenum'] += 1
						else:
							old_line = st.cur_chunk['cur_old_linenum']
							st.cur_chunk['cur_old_linenum'] += 1
							new_line = st.cur_chunk['cur_new_linenum']
							st.cur_chunk['cur_new_linenum'] += 1
						st.cur_chunk['lines'].append({
							'type': t,
							'line': str(m.group(2)),
							'old_num': old_line,
							'new_num': new_line,
						})
						output[:len(m.group(0))] = ''
						continue

					m = re.match('^.+?\n', output)
					if m:
						output[:len(m.group(0))] = ''
						continue

					break

		ret = ProcGit(
			command='diff-tree',
			args=(
				# For the first commit in a repo pretend an empty commit exists before it so we can get a diff for it
				'--root',
				# First output a list of files modified
				'--raw',
				# Don't abbreviate blob hashes in raw format
				'--abbrev=-1',
				# Output a stat of #-lines changed we can use to display things in the ui
				'--numstat',
				# Output a unified diff
				# Be explicit about the 3 lines context so we can let the user control that later.
				# '--unified=%d' % 3,
				# We don't want the default-on one-way text conversion
				# '--no-textconv',
				# Strip the a/ b/ out from paths to make things simple
				# '--no-prefix',
				# Output full sha1s for diffs instead of abbreviated ones
				# '--full-index',
				# Use --no-renames until we implement special handling for copy/rename within diffs
				'--no-renames',
				# Use NUL bytes as terminators instead of munging paths
				'-z',
				# <sha1> of the commit
				commit,
			),
			stdout=stdout,
			git_dir=self.path
		).exit_ok()

		if len(output) > 0:
			raise Exception("Left over output: %s" % output)

		if not ret:
			return None
		return GarethGitDiff(self, st.change)
