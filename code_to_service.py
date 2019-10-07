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

  def get_selected_text(self, service_class_name):
    region = self.view.sel()[0]

    if not region.empty():
      service_code = self.view.substr(region)
      self.create_service_file(service_class_name, service_code)

  def create_service_file(self, service_class_name, service_code):
    source                 = self.view.file_name()
    source_path            = os.path.dirname(source)
    rails_view_path        = os.path.dirname(source_path)
    service_file_with_path = rails_view_path + '/services/' + service_class_name + '.rb'

    class_name     = ''.join(x.capitalize() or '_' for x in service_class_name.split('_'))
    new_class_code = 'class ' + class_name + '\n\n' + ' def initialize(args={})\n\n' + ' end\n\n' + service_code + '\n' + 'end\n'

    if not os.path.exists(service_file_with_path):
      with open(service_file_with_path, 'w') as f:
        f.write(textwrap.dedent(new_class_code))

    self.insert_class_reference(class_name, source)

    self.view.window().open_file(service_file_with_path)

  def insert_class_reference(self, class_name, source):
    region = self.view.sel()[0]

    with Edit(self.view) as edit:
      edit.replace(region, '  ' + class_name + '.new()\n')