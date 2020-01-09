import sys
import os
import re
import material

def test_assetspath():
	with open('{0}{1}base.html'.format(os.path.dirname(material.__file__), os.sep), 'r') as base:
		package = set(re.findall(r'assets/(javascripts/.+\.js|stylesheets/.+\.css|images/icons/.+\.svg)', base.read()))

	with open('{0}{1}{2}{1}material_custom{1}base.html'.format(os.path.dirname(__file__), os.sep, os.path.pardir), 'r') as base:
		custom_file = set(re.findall(r'assets/(javascripts/.+\.js|stylesheets/.+\.css|images/icons/.+\.svg)', base.read()))

	assert package == custom_file, package - custom_file
