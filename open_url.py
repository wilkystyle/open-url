# Quickly open files, folders, web URLs or other URLs from anywhere in Sublime Text
import sublime
import sublime_plugin

import webbrowser
import threading
import os
import re
import subprocess
from urllib.parse import urlparse
from urllib.parse import quote

from .url import is_url


def prepend_scheme(s):
	o = urlparse(s)
	if not o.scheme:
		s = 'http://' + s
	return s


def remove_trailing_delimiters(url, trailing_delimiters):
	"""Removes any and all chars in trailing_delimiters from end of url.
	"""
	if not trailing_delimiters:
		return url
	while url:
		if url[-1] in trailing_delimiters:
			url = url[:-1]
		else:
			break
	return url


def match_openers(openers, url):
	ret = []
	platform = sublime.platform()
	for opener in openers:
		pattern = opener.get('pattern')
		o_s = opener.get('os')
		if pattern and not re.search(pattern, url):
			continue
		if o_s and not o_s.lower() == platform:
			continue
		ret.append(opener)
	return ret


class OpenUrlCommand(sublime_plugin.TextCommand):
	def run(self, edit=None, url=None, show_menu=True):
		self.config = sublime.load_settings('open_url.sublime-settings')

		# Sublime Text has its own open_url command used for things like Help > Documentation
		# so if a url is passed, open it instead of getting text from the view
		if url is None:
			url = self.get_selection()
		path = self.abs_path(url)

		if os.path.isfile(path):
			self.file_action(path, show_menu)
			return

		if os.path.isdir(path):
			self.folder_action(path, show_menu)
			return

		clean = remove_trailing_delimiters(url, self.config.get('trailing_delimiters'))
		if is_url(clean):
			self.open_tab(prepend_scheme(clean))
			return

		openers = match_openers(self.config.get('other_custom_commands'), url)
		if openers:
			self.other_action(url, openers, show_menu)
			return

		self.modify_or_search_action(url)

	def get_selection(self):
		"""Returns selection. If selection contains no characters, expands it
		until hitting delimiter chars.
		"""
		s = self.view.sel()[0]

		start = s.begin()
		end = s.end()

		if start != end:
			return self.view.substr(sublime.Region(start, end)).strip()

		# nothing is selected, so expand selection to nearest delimeters
		view_size = self.view.size()
		delimeters = list(self.config.get('delimiters'))

		# move the selection back to the start of the url
		while start > 0:
			if self.view.substr(start - 1) in delimeters:
				break
			start -= 1

		# move end of selection forward to the end of the url
		while end < view_size:
			if self.view.substr(end) in delimeters:
				break
			end += 1
		return self.view.substr(sublime.Region(start, end)).strip()

	def abs_path(self, path):
		"""Normalizes path, and attempts to convert path into absolute path.
		"""
		path = os.path.normcase(os.path.expandvars(os.path.expanduser(path)))
		if os.path.isabs(path):
			return path

		file_path = self.view.file_name()
		if file_path:  # this file has been saved to disk
			abs_path = os.path.join(os.path.dirname(file_path), path)
			if os.path.exists(abs_path):  # if file relative to current view exists, open it, else continue
				return abs_path

		project = self.view.window().project_data()
		if project is None:  # nothing more to try
			return path
		try:  # look for file relative to project root
			return os.path.join(os.path.expanduser(project['folders'][0]['path']), path)
		except (KeyError, IndexError):
			return path

	def run_subprocess(self, args, kwargs):
		"""Runs on another thread to avoid blocking main thread.
		"""
		def sp(args, kwargs):
			subprocess.check_call(args, **kwargs)
		threading.Thread(target=sp, args=(args, kwargs)).start()

	def open_tab(self, url):
		browser = self.config.get('web_browser', '')

		def ot(url, browser):
			try:
				controller = webbrowser.get(browser or None)
			except:
				e = 'Python couldn\'t find the "{}" browser. Change "web_browser" in Open URL\'s settings.'
				sublime.error_message(e.format(browser or 'default'))
				return
			controller.open_new_tab(url)
		threading.Thread(target=ot, args=(url, browser)).start()

	def modify_or_search_action(self, term):
		"""Not a URL and not a local path; prompts user to modify path and looks
		for it again, or searches for this term using a web searcher.
		"""
		searchers = self.config.get('web_searchers', [])
		opts = ['modify path ({})'.format(term)]
		opts += ['{} ({})'.format(s['label'], term) for s in searchers]
		sublime.active_window().show_quick_panel(opts, lambda idx: self.modify_or_search_done(idx, searchers, term))

	def modify_or_search_done(self, idx, searchers, term):
		if idx < 0:
			return
		if idx == 0:
			self.view.window().show_input_panel('URL or path:', term, self.url_search_modified, None, None)
			return
		idx -= 1
		searcher = searchers[idx]
		self.open_tab('{}{}'.format(
			searcher.get('url'),
			quote(term.encode(searcher.get('encoding', 'utf-8'))),
		))

	def url_search_modified(self, text):
		"""Call open_url again on modified path.
		"""
		try:
			self.view.run_command('open_url', {'url': text})
		except ValueError:
			pass

	def other_action(self, path, openers, show_menu):
		if openers and not show_menu:
			self.folder_done(0, openers, path)
			return

		opts = [opener.get('label') for opener in openers]
		sublime.active_window().show_quick_panel(opts, lambda idx: self.other_done(idx, openers, path))

	def other_done(self, idx, openers, path):
		if idx < 0:
			return
		opener = openers[idx]
		self.run_subprocess(opener.get('commands', []) + [path], opener.get('kwargs', {}))

	def folder_action(self, folder, show_menu):
		"""Choose from folder actions.
		"""
		openers = self.config.get('folder_custom_commands', [])

		if openers and not show_menu:
			self.folder_done(0, openers, folder)
			return

		opts = [opener.get('label') for opener in openers]
		sublime.active_window().show_quick_panel(opts, lambda idx: self.folder_done(idx, openers, folder))

	def folder_done(self, idx, openers, folder):
		if idx < 0:
			return
		opener = openers[idx]
		if sublime.platform() == 'windows':
			folder = os.path.normcase(folder)
		self.run_subprocess(opener.get('commands', []) + [folder], opener.get('kwargs', {}))

	def file_action(self, path, show_menu):
		"""Edit file or choose from file actions.
		"""
		openers = match_openers(self.config.get('file_custom_commands'), path)

		if not show_menu:
			self.view.window().open_file(path)
			return

		sublime.active_window().show_quick_panel(
			['edit'] + [opener.get('label') for opener in openers],
			lambda idx: self.file_done(idx, openers, path),
		)

	def file_done(self, idx, openers, path):
		if idx < 0:
			return
		if idx == 0:
			self.view.window().open_file(path)
			return

		opener = openers[idx-1]
		if sublime.platform() == 'windows':
			path = os.path.normcase(path)
		self.run_subprocess(opener.get('commands', []) + [path], opener.get('kwargs', {}))
