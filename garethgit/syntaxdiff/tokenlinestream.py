from collections import Iterator
import re

class TokenLineStreamLine(Iterator):
	def __init__(self, line_stream):
		self.line_stream = line_stream
		self.eol = False
		self._cache = None

	def _precache(self):
		if self.eol:
			return

		self._cache = iter([token for token in self])

	def _next_token(self):
		return self.line_stream._next_token()

	def next(self):
		if self._cache:
			return next(self._cache)
		# This is the primary handling
		# Note that eol is isgnored if _cache is setup
		if self.eol:
			raise StopIteration
		ttype, ttext = self._next_token()
		m = re.match('^(.*?(?:\r\n|\r|\n))(.*)$', ttext, re.DOTALL)
		if m:
			if len(m.group(2)) > 0:
				self.line_stream.last_token = (ttype, m.group(2))
			ttext = m.group(1)
			self.eol = True
		return (ttype, ttext)

class TokenLineStream(Iterator):
	def __init__(self, token_stream):
		self.token_stream = token_stream
		self.last_token = None
		self.last_line = None

	def _next_token(self):
		if self.last_token is not None:
			token = self.last_token
			self.last_token = None
			return token
		return next(self.token_stream)

	def next(self):
		if self.last_line:
			# Because we work with a linear stream if we're asked for the next line before
			# The last line is finished we need to tell the last line to read all the tokens it needs right now
			self.last_line._precache()
		self.last_line = None
		# We intentionally do not wrap this in a StopIteration try:
		# If no more tokens can be found then then StopIteration falls through indicating that there are no more lines
		# If there IS a token we automatically save it back to last_token so that it can be read by the line object we
		# will create next.
		self.last_token = self._next_token()
		self.last_line = TokenLineStreamLine(self)
		return self.last_line
