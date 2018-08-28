# Open URL


## Description
Quickly open files, folders, web URLs or other URLs from anywhere in Sublime Text.


## Install
Look for __Open URL__ using the [Package Manager](http://wbond.net/sublime_packages/package_control)


## How to use
Put the cursor inside a __file__ / __folder__ / __URL__ / __word__ and run the command. It automatically expands the selection until it hits __delimiter__ chars, which can be changed in the settings (see below).

Alternatively, highlight the text you want to open. If text is highlighted the selection is not expanded.

Here's a bunch of ways you can run the command.

- <kbd>ctrl+u</kbd>
- right-click > __Open URL__
- </kbd>alt</kbd> + double-click
- <kbd>shift+cmd+p</kbd>, then look for __Open URL__


### Give it a try
Copy the items below to Sublime Text. Place your cursor inside any one of them and hit <kbd>ctrl+u</kbd>.

- $HOME/Desktop
- <https://news.ycombinator.com>
- google.com
- search_for_me


### How does it work?
If your selection is a __file__ or a __folder__, you can choose to __edit__ it (open with Sublime Text), or __reveal__ it (open with macOS Finder/Windows File Explorer/Linux File Manager).

Opening files and folders is super convenient. Both can be specified with absolute paths, paths relative to the currently open file, or paths relative to the root of the currently open project. Env vars and the alias `~` are expanded.

If your selection is a URL, it opens immediately in a new tab in your default web browser. You can omit the scheme (http://) if you want and __Open URL__ will add it for you.

If your selection is none of the above, you'll be presented with two options:

- modify the selection and try again
- search for the selection using one of your configured __web_searchers__
  + the only web searcher that ships with __Open URL__ is Google search
  + to add others, read more in the "Settings" section below


### Shortcuts
Don't want to choose from menu items to open a file or a folder? Look for __Open URL (Skip Menu)__ in the Command Palette. To create a key binding for this, open __Preferences: Key Bindings__ from the Command Palette, and add the following:

~~~json
{ "keys": ["your+key+binding"], "command": "open_url", "args": { "show_menu": false } },
~~~

This will open files in Sublime Text for editing, or reveal folders in the Finder, without showing the menu first.


### Running commands on files, folders or special URLs
__Open URL__ provides a few settings you can configure to run custom commands on files, folders, or special URLs, such as FTP URLs:

- __file_custom_commands__
- __folder_custom_commands__
- __other_custom_commands__

Read more below.


## Settings
To customize these, hit <kbd>shift+cmd+p</kbd> to open the Command Palette, and look for __Open URL: Settings__.

- __delimeters__
  + characters at which auto-expansion of selected path stops, e.g. ` \t\n\r\"',*<>[]()`
  + the default settings are Markdown friendly
- __trailing_delimiters__
  + if any of these characters are seen at the end of a web URL, they are recursively removed; default is `;.:`
- __web_browser__
  + the browser that Open URL uses to open new tabs; must be a string [from this list](https://docs.python.org/3.3/library/webbrowser.html)
  + if you use an empty string, the "default browser" will be used
  + if you choose a browser that's not installed on your machine, Open URL will complain
- __web_searchers__
  + if your selection isn't a file, a folder, or a URL, you can choose to pass it to a web searcher, which is just a URL that searches for the selected text
  + example: `{ "label": "google search", "url": "http://google.com/search?q=", "encoding": "utf-8" }`
- __file_custom_commands__
  + pass a file to one or more shell commands whose patterns match the file path to shell commands; run in a subprocess
  + example: `{ "label": "open with default app", "pattern": "\\.pdf$|\\.png$", "commands": [ "open" ] },`
- __folder_custom_commands__
  + pass a folder to any of these shell commands; run in a subprocess
  + example: `{ "label": "open in terminal", "commands": [ "open", "-a", "/Applications/iTerm.app" ] }`
- __other_custom_commands__
  + pass a URL which is neither a file, a directory, nor a web URL to one or more shel commands whose patterns match the URL; run in a subprocess
  + e.g., for opening FTP URLs: `{ "label": "open with filezilla", "pattern": "^ftp://", "commands": [ "open", "-a", "/Applications/FileZilla.app" ] },`
- __folder_extra_commands__
  + set to this to `false` if you want to disable the following folder commands: ('add to sublime project', 'new sublime window')
- __file_extra_commands__
  + set to this to `false` if you want to disable the following file commands: ('run', 'new sublime window', 'system open')


## Finally
See also: [Google Spell Check](https://github.com/noahcoad/google-spell-check).

Credits: Thanks goes to peterc for starting [a forum thread](http://www.sublimetext.com/forum/viewtopic.php?f=2&t=4243) about this topic and KatsuomiK for [his gist](https://gist.github.com/3542836), which were the inspiration for this plugin.

Author: [@noahcoad](http://twitter.com/noahcoad) writes software for the heck of it and to make life just a little more efficient.

Maintainer: [@kylebebak](https://github.com/kylebebak).
