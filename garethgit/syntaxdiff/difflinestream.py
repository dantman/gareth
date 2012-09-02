import re

# This method isn't working out; We should try implementing a bunch of different diff handlers and
# try them all out.
# - A character based diff_match_patch
# - A character based difflib.SequenceMatcher
# - A line based difflib.SequenceMatcher
# - A character based bzrlib Patience diff (can this do line diff too?)
# Note: Patience diff extends SequenceMatcher, we can use the same code for both by making the matcher a tweakable variable

	# diff = diff_match_patch()
	# diff_stream = diff.diff_main(old_blob, new_blob)
	# diff.diff_cleanupSemantic(diff_stream)
	# diff_line_stream = DiffLineStream(diff_stream)
