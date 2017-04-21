import sublime
import sublime_plugin


class PrintLineCommand(sublime_plugin.TextCommand):
	def run(self, edit, length, char):
		for sel in self.view.sel():
			selText = self.view.substr(sel)
			if len(selText) % 2 == 1:
				selText+= " "
				
			numChars = int((length - len(selText)) / 2)
			finishedStr = char * numChars + selText + char * numChars

			self.view.replace(edit, sel, finishedStr)
		#self.view.insert(edit, 0, self.view.sel())
