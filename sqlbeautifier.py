import logging
import sublime
import sublime_plugin
import subprocess
import tempfile
# import os
# os.system('export PATH="/Users/adam/code/anaconda/bin:$PATH"')

# for ST2
settings = sublime.load_settings('SQL Beautifier.sublime-settings')


# for ST3
def plugin_loaded():
    global settings
    settings = sublime.load_settings('SQL Beautifier.sublime-settings')


class SqlBeautifierCommand(sublime_plugin.TextCommand):
    setting_kwds = (
        'keyword_case',
        'identifier_case',
        'reindent',
        'indent_width')

    settings_bool = (
        'strip_comments',
        'reindent_aligned',
        'use_space_around_operators')

    def _settings_to_argparse(self):
        args = []
        for k in self.setting_kwds:
            val = settings.get(k)
            if val is not None:
                args.append('--{} {}'.format(str(k), str(val)))
        for k in self.settings_bool:
            val = settings.get(k)
            if val:
                args.append('--{}'.format(str(k)))
        return ' '.join(args)

    def format_sql(self, raw_sql):
        try:
            fnm = '/tmp/sqlformat.tmp'
            with open(fnm, 'w+') as tmp:
                tmp.write(raw_sql)
            cmd = 'sqlformat {} {}'.format(fnm, self._settings_to_argparse())
            out = subprocess.check_output(cmd, shell=True, universal_newlines=True)
            return str(out)
        except Exception as e:
            logging.exception(e)
            return None

    def replace_region_with_formatted_sql(self, edit, region):
        selected_text = self.view.substr(region)
        foramtted_text = self.format_sql(selected_text)
        self.view.replace(edit, region, foramtted_text)

    def run(self, edit):
        for region in self.view.sel():
            if region.empty():
                selection = sublime.Region(0, self.view.size())
                self.replace_region_with_formatted_sql(edit, selection)
                self.view.set_syntax_file("Packages/SQL/SQL.tmLanguage")
            else:
                self.replace_region_with_formatted_sql(edit, region)
