
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# class InvalidString(str):
# 	def __mod__(self, other):
# 		from django.template.base import TemplateSyntaxError
# 		raise TemplateSyntaxError(
# 			"Undefined variable, unknown value, or exception for: %s" % other)

# TEMPLATE_STRING_IF_INVALID = InvalidString("%s")
