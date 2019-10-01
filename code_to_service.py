import os, re, textwrap
import sublime, sublime_plugin

try:
  from .Edit import Edit as Edit
except:
  from Edit import Edit as Edit

class CodeToServiceCommand(sublime_plugin.TextCommand):

  def run(self, edit):
    self.edit = edit
    self.view.window().show_input_panel("Service object name:", "", self.get_selected_text, None, None)

  def get_selected_text(self, partial_name):
    region = self.view.sel()[0]

    if not region.empty():
      partial_code = self.view.substr(region)
      self.create_partial_file(partial_name, partial_code)

  def create_partial_file(self, partial_name, partial_code):
    source                 = self.view.file_name()
    source_path            = os.path.dirname(source)
    rails_view_path        = os.path.dirname(source_path)
    partial_file_with_path = rails_view_path + '/services/' + partial_name + '.rb'

    class_name     = ''.join(x.capitalize() or '_' for x in partial_name.split('_'))
    new_class_code = 'class ' + class_name + '\n\n' + ' def initialize(args={})\n\n' + ' end\n\n' + partial_code + '\n' + 'end\n'

    if not os.path.exists(partial_file_with_path):
      with open(partial_file_with_path, 'w') as f:
        f.write(textwrap.dedent(new_class_code))

    self.insert_class_reference(class_name, source)

    self.view.window().open_file(partial_file_with_path)

  def insert_class_reference(self, class_name, source):
    region = self.view.sel()[0]

    with Edit(self.view) as edit:
      edit.replace(region, '  ' + class_name + '.new()\n')