import sublime, sublime_plugin, os, threading

class GotoRecentListener(sublime_plugin.EventListener):
  def on_activated(self, view):
    if view.file_name():
      view.window().run_command("goto_recent", { "file_name": view.file_name() })

  def on_close(self, view):
    if view.file_name():
      for window in sublime.windows():
        window.run_command("goto_recent", { "file_name": view.file_name(), "remove": True })

class GotoRecentCommand(sublime_plugin.WindowCommand):
  def __init__(self, window):
    sublime_plugin.WindowCommand.__init__(self, window)

    try:
      window.recent_files.size()
    except AttributeError:
      window.recent_files = []
      window.combined_files = []

    # Pre-populate with already opened files
    for view in window.views():
      self.add_file(view.file_name())

  def relative_file(self, file_name):
    folders = self.window.folders()[:]
    folders.sort(key = len)
    folders.reverse()

    for folder in folders:
      if file_name.startswith(folder):
        return os.path.basename(folder) + file_name[len(folder):]
    return file_name

  def add_file(self, file_name):
    relative = self.relative_file(file_name)

    if relative in self.window.recent_files:
      self.window.recent_files.remove(relative)

    self.window.recent_files.insert(0, relative);

  def remove_file(self, file_name):
    relative = self.relative_file(file_name)

    if relative in self.window.recent_files:
      self.window.recent_files.remove(relative)


  def absolute_file(self, relative_file):
    folders = self.window.folders()[:]
    folders.sort(key = len)
    folders.reverse()

    first_folder = ""
    index = relative_file.find("/")

    if index >= 0:
      first_folder = relative_file[0:index]

    for folder in folders:
      if os.path.basename(folder) == first_folder:
        return os.path.dirname(folder) + "/" + relative_file

    return relative_file

  def selected(self, index):
    if index >= 0:
      target_file  = self.absolute_file(self.window.combined_files[index])
      self.window.open_file(target_file)
      self.run(target_file)

  def run(self, file_name=None, remove=False):
    if file_name:
      if remove:
        self.remove_file(file_name)
      else:
        self.add_file(file_name)
    else:
      self.show_panel()

  def show_panel(self):
    self.window.combined_files = []

    for item in self.window.recent_files:
      self.window.combined_files.append(item)

    active_file = None
    if len(self.window.combined_files) > 0:
      active_file = self.absolute_file(self.window.combined_files.pop(0))

    for folder in self.window.folders():
      for root, subFolders, files in os.walk(folder):
        for file in files:
          file_path = self.relative_file(os.path.join(root,file))
          if active_file != None and file_path == active_file: continue
          if file_path.find("/.") >= 0 : continue
          if not file_path in self.window.combined_files:
            self.window.combined_files.append(file_path)

    self.window.show_quick_panel(self.window.combined_files, self.selected)
