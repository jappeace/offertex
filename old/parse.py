#!/usr/bin/python
# This program parses the offer.tex file to produce a copy where the variables are filled in.
# Copyright (C) 2016 Jappe Klooster

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
# GNU General Public License for more details. 
# You should have received a copy of the GNU General Public License
# along with this program.If not, see <http://www.gnu.org/licenses/>.


import re

import jinja2 as jin
import jinmeta as meta

class Parser:
    """
        Does parsing with jinja. Loads the main template environment and
        provides some utility methods on that
    """

    def __init__(self, path):
        self.environment = _createLatexEnvironment(path)

    def get_undeclared_vars_from_file(self, filename):
        """
            returns a list of undeclared vars from a file,
            in order of decleration
        """
        template_source = self.environment.loader.get_source(self.environment, filename)[0]
        return self.get_undeclared_vars_from_string(template_source)

    def get_undeclared_vars_from_string(self, string):
        """Gets undeclared vars from a string (jinja source)"""
        parsed_content = self.environment.parse(string)
        return meta.filter_out_built_ins(
            meta.find_undeclared_variables_in_order(parsed_content)
        )
    def render_file(self, filename, symbols):
        """render a particular jinjia file with symbols"""
        return _render(self.environment.get_template(filename), symbols)

    def render_string(self, string, symbols):
        """render a string with symbols"""
        
        return _render(self.environment.from_string(string), symbols)

def _render(template, symbols):
    """cal render on jinjia template (api wrapper)"""
    return template.render(symbols)

_latex_substitutes = [
    (re.compile(r'\\'), r'\\textbackslash'),
    (re.compile(r'([{}_#%&$])'), r'\\\1'),
    (re.compile(r'~'), r'\~{}'),
    (re.compile(r'\^'), r'\^{}'),
    (re.compile(r'"'), r"''"),
    (re.compile(r'\.\.\.+'), r'\\ldots'),
]
def _escape_tex(value):
    """replaces stuff in latex thats difficult for jinja"""
    newval = value
    for pattern, replacement in _latex_substitutes:
        newval = pattern.sub(replacement, newval)
    return newval

def _createLatexEnvironment(path):
    """Creates an environment specifically aimed at latex"""
    texenv = jin.Environment(
        loader=jin.FileSystemLoader(path),
        enable_async=False
    )
    texenv.block_start_string = '<='
    texenv.block_end_string = '=>'
    texenv.variable_start_string = '<?'
    texenv.variable_end_string = '?>'
    texenv.comment_start_string = '<!--'
    texenv.comment_end_string = '-->'
    texenv.filters['escape_tex'] = _escape_tex
    return texenv

