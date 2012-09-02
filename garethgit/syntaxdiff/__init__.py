from pygments.token import STANDARD_TYPES
from pygments.lexers import guess_lexer_for_filename
from pygments.util import ClassNotFound
from django.utils.encoding import smart_str
from django.utils.html import escape
from garethgit.syntaxdiff.tokenlinestream import TokenLineStream
from garethgit.syntaxdiff.difftool import diff, line_list
from base64 import b64encode
import re

def render_box(old_path, new_path, icon, do_render):
	out = bytearray('')
	out.extend('<div class="diff highlight">')
	out.extend('<div class="diff-header">')
	out.extend('<span class="fileicon"><i class="icon-%s"></i></span>' % icon)
	out.extend(smart_str(escape(old_path)))
	if old_path != new_path:
		out.extend(' -> ')
		out.extend(smart_str(escape(new_path)))
	out.extend('</div>')
	out.extend('<div class="diff-wrapper">')
	try:
		sub_out = bytearray('')
		do_render(sub_out)
		out.extend(sub_out)
	except Exception, e:
		out.extend('<table class="diff-any">')
		out.extend('<td class="same num"></td>')
		out.extend('<td class="same line">')
		out.extend('<p>Could not render diff.</p>')
		import traceback
		out.extend('<pre>')
		out.extend(traceback.format_exc())
		out.extend('</pre>')
		out.extend('</td>')
		out.extend('</tr>')
		out.extend('</table>')
	out.extend('</div>')
	out.extend('</div>')
	return smart_str(out)

def render(old_path, old_blob, new_path, new_blob):

	old_type = None
	new_type = None
	try:
		from magic import Magic
		mag = Magic(mime=True)
		if old_blob:
			old_type = mag.from_buffer(old_blob)
		if new_blob:
			new_type = mag.from_buffer(new_blob)
	except ImportError:
		pass

	types = []
	if old_type:
		types.append(old_type)
	if new_type:
		types.append(new_type)

	if len([t for t in types if t.startswith('image/')]) > 1:
		"""
		Image diff.
		"""
		icon = 'picture'
		def do_render(out):
			out.extend('<table class="diff-any diff-sidebyside diff-image">')
			out.extend('<td class="left old num"></td>')
			out.extend('<td class="left old line">')
			if old_blob:
				data = "data:%s;base64,%s" % (old_type, b64encode(old_blob))
				out.extend('<img alt="" src="%s">' % smart_str(escape(data)))
			out.extend('</td>')
			out.extend('<td class="right new num"></td>')
			out.extend('<td class="right new line">')
			if new_blob:
				data = "data:%s;base64,%s" % (new_type, b64encode(new_blob))
				out.extend('<img alt="" src="%s">' % smart_str(escape(data)))
			out.extend('</td>')
			out.extend('</tr>')
			out.extend('</table>')
	else:
		"""
		Text diff.
		"""
		old_token_lines = ()
		new_token_lines = ()
		try:
			"""
			Syntax highlighting for the old text.
			"""
			if old_blob:
				old_lexer = guess_lexer_for_filename(old_path, old_blob)
				old_tokens = old_lexer.get_tokens(old_blob)
				old_token_lines = TokenLineStream(old_tokens)
		except ClassNotFound:
			pass

		try:
			"""
			Syntax highlighting for the new text.
			"""
			if new_blob:
				new_lexer = guess_lexer_for_filename(new_path, new_blob)
				new_tokens = new_lexer.get_tokens(new_blob)
				new_token_lines = TokenLineStream(new_tokens)
		except ClassNotFound:
			pass

		if old_blob is not None and new_blob is not None:
			"""
			Normal two sided diff
			"""
			icon = 'edit'
			def do_render(out):
				diff_line_stream = diff(old_blob, new_blob)
				render_side_diff(out, diff_line_stream, (old_token_lines, new_token_lines))

		elif old_blob is not None:
			"""
			One sided deletion diff.
			"""
			icon = 'trash'
			def do_render(out):
				render_blob(out, -1, old_blob, old_token_lines)

		elif new_blob is not None:
			"""
			One sided creation diff.
			"""
			icon = 'file'
			def do_render(out):
				render_blob(out, 1, new_blob, new_token_lines)

		else:
			"""
			No sided diff. eg: Metadata change.
			"""
			icon = 'question-sign'
			def do_render(out):
				out.extend("No data")

	return render_box(old_path, new_path, icon, do_render)

def line_to_html(text):
	html = smart_str(escape(text))
	html = html.replace('\t', '<span class="tab">\t</span>')
	return html

def line_out(out, line, side=None):
	if len(line) >= 4:
		dtype, num, chunks, syntax_chunks = line
	else:
		dtype, num, chunks = line
		syntax_chunks = None
	if not chunks:
		ltype = "nil"
	elif dtype == -1:
		ltype = "old"
	elif dtype == 1:
		ltype = "new"
	else:
		ltype = "same"

	if side:
		side = "%s " % side
	else:
		side = ""

	errors = []

	out.extend('<td class="%s%s num">' % (side, ltype))
	if num is not None:
		out.extend(smart_str(escape(num)))
	out.extend('</td>')
	out.extend('<td class="%s%s line">' % (side, ltype))
	if chunks:
		for ddt, text in chunks:
			if ddt == -1:
				out.extend('<del>')
			elif ddt == 1:
				out.extend('<ins>')
			if syntax_chunks:
				syntax_chunks = list(syntax_chunks)
				while len(text) > 0:
					if len(syntax_chunks) <= 0:
						error = "Chunk overflow error '%s' does not have a syntax chunk" % smart_str(text)
						print error
						errors.append(error)
						out.extend(line_to_html(text))
						text = ''
						continue
					syntax_type, syntax_text = syntax_chunks.pop(0)
					if len(syntax_text) > len(text):
						# If the syntax chunk is larger than the diff chunk then prepend a new syntax chunk with the remainder
						syntax_chunks.insert(0, (syntax_type, syntax_text[len(text):]))
						syntax_text = syntax_text[:len(text)]
					subchunk_text = text[:len(syntax_text)]
					text = text[len(syntax_text):] # Trim the initial text off the chunk text
					if syntax_text == subchunk_text:
						cls = ''
						fname = STANDARD_TYPES.get(syntax_type)
						if fname:
							cls = fname
						else:
							aname = ''
							while fname is None:
								aname = '-' + syntax_type[-1] + aname
								syntax_type = syntax_type.parent
								fname = STANDARD_TYPES.get(syntax_type)
							cls = fname + aname

						if cls:
							out.extend('<span class="%s">' % " ".join(cls))
							out.extend(line_to_html(subchunk_text))
							out.extend('</span>')
						else:
							out.extend(line_to_html(subchunk_text))
					else:
						# Chunk mismatch (code error)
						error = "Chunk mismatch error '%s' does not match '%s'" % (smart_str(syntax_text), smart_str(subchunk_text))
						print error
						errors.append(error)
						out.extend(line_to_html(subchunk_text))

			else:
				out.extend(line_to_html(text))
			if ddt == -1:
				out.extend('</del>')
			elif ddt == 1:
				out.extend('</ins>')
	for error in errors:
		out.extend('<br>')
		out.extend('<span class="error differror">')
		out.extend(smart_str(escape(error)))
		out.extend('</span>')
	out.extend('</td>')

def render_blob(out, dtype, blob, token_lines):
	out.extend('<table class="diff-any diff-oneway">')
	num = 1
	if blob:
		for line in line_list(blob):
			token_line = None
			if token_lines:
				token_line = next(token_lines, None)
			out.extend('<tr>')
			line_out(out, (dtype, num, ((0, line),), token_line))
			out.extend('</tr>')
			num += 1
	else:
		out.extend('<tr>')
		line_out(out, (dtype, None, ((0, "Empty file"),)))
		out.extend('</tr>')
	out.extend('</table>')

def diffline_syntax_combine(line, token_lines):
	dtype, num, chunks = line
	token_line = None
	if token_lines:
		token_line = next(token_lines, None)
	return (dtype, num, chunks, token_line)

def render_side_diff(out, diff_line_stream, token_lines):
	old_token_lines, new_token_lines = token_lines
	out.extend('<table class="diff-any diff-sidebyside">')
	for old_line, new_line in line_diff_pairs(diff_line_stream):
		old_line = diffline_syntax_combine(old_line, old_token_lines)
		new_line = diffline_syntax_combine(new_line, new_token_lines)
		out.extend('<tr>')
		line_out(out, old_line, 'left')
		line_out(out, new_line, 'right')
		out.extend('</tr>')
	out.extend('</table>')

def line_diff_pairs(diff_line_stream):
	"""
	Takes a diff line stream and generates a stream of line pairs suitable
	for use in the creation of a side-by-side diff
	"""
	old_cache = []
	new_cache = []
	old_num = 1
	new_num = 1
	for dtype, line in diff_line_stream:
		if dtype == 0:
			while len(old_cache) > 0 and len(new_cache) > 0:
				yield ((-1, old_num, old_cache.pop(0)), (1, new_num, new_cache.pop(0)))
				old_num += 1
				new_num += 1
			while len(old_cache) > 0:
				yield ((-1, old_num, old_cache.pop(0)), (0, None, None))
				old_num += 1
			while len(new_cache) > 0:
				yield ((0, None, None), (1, new_num, new_cache.pop(0)))
				new_num += 1
			yield ((0, old_num, line), (0, new_num, line))
			old_num += 1
			new_num += 1
		elif dtype == -1:
			old_cache.append(line)
		elif dtype == 1:
			new_cache.append(line)
	# Ensure that trailing deletions/insertions are outputted
	while len(old_cache) > 0 and len(new_cache) > 0:
		yield ((-1, old_num, old_cache.pop(0)), (1, new_num, new_cache.pop(0)))
		old_num += 1
		new_num += 1
	while len(old_cache) > 0:
		yield ((-1, old_num, old_cache.pop(0)), (0, None, None))
		old_num += 1
	while len(new_cache) > 0:
		yield ((0, None, None), (1, new_num, new_cache.pop(0)))
		new_num += 1
