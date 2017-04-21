import sublime, sublime_plugin, re, os

#This is pretty hacky code and will probably break if you try and get cheeky with it
#It's intended more as a proof of concept more than an actual plugin

#Poor mans HTMLParser
class ParseHTML:
	def __init__(self):
		self.line = ()

	def __init__(self, line):
		self.line = iter(line)

	def generate(self):
		openTag = False
		closeTag = False
		quote = False
		elementTag = False
		element = ""
		attr = ""
		value = ""
		lastChar = ""

		for char in self.line:
			if char == "\"" and lastChar != "\\":
				quote = not quote
				attr += char
			elif quote:
				attr += char
			elif char == "<":
				closeTag = False
				if (value != ""):
					yield value, "value"
				openTag = True
				element += char
			elif char == ">":
				closeTag = True
				elementTag = False
				quote = False
				if (openTag):
					element += char
					yield element, "element"
				else:
					element = ""
					if (attr == "/"):
						attr == ""
					else:
						yield attr, "attr"
			elif char == " ":
				if openTag:
					yield element, "element"
					openTag = False
					elementTag = True
				elif quote == False:
					if closeTag:
						value+= char
					else:
						yield attr, "attr"
						attr = ""
				elif quote:
					attr += char
			elif elementTag:
				attr += char
			elif openTag:
				element += char
			elif closeTag:
				value += char
			lastChar = char

class FormatHtmlCommand(sublime_plugin.TextCommand):
	def __init__(self, other):
		super().__init__(other)

	def run(self, edit):
		bigRegion = self.view.line(self.view.sel()[0])

		for region in self.view.sel():
			textRegion = str(self.view.substr(self.view.line(region)))
			line = textRegion.replace("\t", "")
			tabs = len(textRegion) - len(line)
			line = line.replace("  ", " ")
			if (re.match(r'\<[A-Za-z\-\_]+((\s[A-Za-z\-\_]+)(\=[\"\'][A-Za-z0-9\-\_\.\,\$\(\)\=\s\'\;\:\<\>\&\{\}\*\+]*[\"\'])?)*(\s)*(\/)?\>', line)):
				self.hp = ParseHTML(line)
				data = list(self.hp.generate())

				elements = []
				attrs = []
				values = []
				displayText = ""

				for value in data:
					if (value[1] == "element"):
						elements.append("\t" * tabs + value[0] + "\n")
					elif (value[1] == "attr"):
						attrs.append("\t" * (tabs + 1) + value[0] + "\n")
					elif (value[1] == "value"):
						values.append("\t" * (tabs + 2) + value[0] + "\n")

				if (len(elements) > 2):
					return
				else:
					displayText += elements[0]
					attrs = sorted(attrs)
					attrs[-1] = attrs[-1][:-1]
					if (len(elements) == 1):
						attrs[-1] = attrs[-1] + "/>\n"
					else:
						attrs[-1] = attrs[-1] + ">\n"
					displayText += "".join(attrs)
					displayText += "".join(values)
					if (len(elements) == 2):
						displayText += elements[1]

				self.view.replace(edit, bigRegion, displayText)
