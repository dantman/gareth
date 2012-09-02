from collections import Iterator
from difflib import SequenceMatcher
import re

class EngineException(Exception):
	pass

def diff(old, new, engine='difflib-line'):
	if engine == 'difflib-char':
		diff_stream = SequenceMatcherStream(old, new)
		return DiffLineStream(diff_stream)

	if engine == 'difflib-line':
		return DiffSequenceLineMatcherStream(old, new)

	if engine == 'diff-match-patch':
		diff_stream = DiffMatchPatchStream(old, new)
		return DiffLineStream(diff_stream)

	raise EngineException("The engine %s does not exist." % engine)

def SequenceMatcherStream(a, b, Matcher=SequenceMatcher):
	"""
	This creates an iterable diff stream in the same format as what
	Google's Diff-Match-Patch uses.
	The matcher it uses can be configured with the Matcher option.
	"""
	sm = Matcher()
	sm.set_seqs(a, b)
	for tag, a1, a2, b1, b2 in sm.get_opcodes():
		if tag == "replace":
			yield (-1, a[a1:a2])
			yield (1, b[b1:b2])
		elif tag == "delete":
			yield (-1, a[a1:a2])
		elif tag == "insert":
			yield (1, b[b1:b2])
		elif tag == "equal":
			yield (0, a[a1:a2])
		else:
			raise Exception("Unknon opcode %s" % tag)

def DiffMatchPatchStream(old, new):
	"""
	This outputs Google's Diff-Match-Patch's iterable diff stream.
	"""
	from diff_match_patch import diff_match_patch
	d = diff_match_patch()
	diff_stream = d.diff_main(old, new)
	d.diff_cleanupSemantic(diff_stream)
	return diff_stream

def line_list(string):
	return re.findall('.*?(?:\r\n|\r|\n)|.+$', string)

def DiffSequenceLineMatcherStream(a, b, Matcher=SequenceMatcher, LineMatcher=None, MatcherStream=DiffMatchPatchStream):
	"""
	"""
	if not LineMatcher:
		LineMatcher = Matcher
	# @fixme Stream MUST retain eol chars
	a = line_list(a)
	b = line_list(b)
	sm = Matcher()
	sm.set_seqs(a, b)
	for tag, a1, a2, b1, b2 in sm.get_opcodes():
		if tag == "replace":
			aa = "".join(a[a1:a2])
			bb = "".join(b[b1:b2])
			dd = DiffLineStream(MatcherStream(aa, bb))
			for line in dd:
				yield line
		elif tag == "delete":
			for line in a[a1:a2]:
				yield (-1, ((-1, line),))
		elif tag == "insert":
			for line in b[b1:b2]:
				yield (1, ((1, line),))
		elif tag == "equal":
			for line in a[a1:a2]:
				yield (0, ((0, line),))
		else:
			raise Exception("Unknon opcode %s" % tag)

def DiffLineStream(diff_stream):
	"""
	This converts a character based diff stream into a line diff stream
	by iterating over the diff stream, breaking up tokens by newlines,
	and yielding line diffs containing char diffs.
	"""
	old_line = []
	new_line = []

	for dflag, text in diff_stream:
		while True:
			next_line = None
			m = re.match('^(.*?(?:\r\n|\r|\n))(.*)$', text, re.DOTALL)
			if m:
				text = m.group(1)
				next_line = m.group(2)
			if dflag <= 0:
				old_line.append((dflag, text))
			if dflag >= 0:
				new_line.append((dflag, text))
			if next_line:
				# yield (0, )
				if dflag <= 0:
					yield (-1, old_line)
					old_line = []
				if dflag >= 0:
					yield (+1, new_line)
					new_line = []
				text = next_line
				continue
			break

	if len(old_line) > 0:
		yield (-1, old_line)
	if len(new_line) > 0:
		yield (+1, new_line)
