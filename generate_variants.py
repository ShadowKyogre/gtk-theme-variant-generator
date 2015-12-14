from argparse import ArgumentParser
import configparser
from copy import deepcopy
from os import path
import re
import sys
import shutil

XRESOURCE=re.compile(r'^\*\.(foreground|background|cursorColor|color\d+):\s*(\S+)', re.MULTILINE)

DEFAULT_TERMINAL = {
	'foreground': '#ffffff',
	'background': '#000000',
	'cursorColor':'#ffffff',
	'color0':     '#000000',
	'color1':     '#AA0000',
	'color2':     '#00AA00',
	'color3':     '#AA5500',
	'color4':     '#0000AA',
	'color5':     '#AA00AA',
	'color6':     '#00AAAA',
	'color7':     '#AAAAAA',
	'color8':     '#555555',
	'color9':     '#FF5555',
	'color10':    '#55FF55',
	'color11':    '#FFFF55',
	'color12':    '#5555FF',
	'color13':    '#FF55FF',
	'color14':    '#55FFFF',
	'color15':    '#FFFFFF',
}

def import_xresources(fpath):
	output = deepcopy(DEFAULT_TERMINAL)
	with open(fpath, 'r', encoding='utf-8') as f:
		textctnt = f.read()
		for k, v in XRESOURCE.findall(textctnt):
			output[k]=v
	return output


if __name__ == "__main__":
	aparser = ArgumentParser()
	aparser.add_argument('--xresources', '-x',
	                     default=None,
	                     help='Read colors from an xrdb file')
	aparser.add_argument('--config-file',  '-c',
	                     default=path.join(path.dirname(__file__), 'variants.conf'),
	                     help='Look for replacement hints and variants with the alternate config file')
	aparser.add_argument('--input-dir',  '-i',
	                     default=path.join(path.dirname(__file__), 'templates'),
	                     help='Input directory for themes to make variants of')
	aparser.add_argument('--output-dir', '-o',
	                     default=path.join(path.dirname(__file__), 'output'),
	                     help='Output directory for variants')
	args = aparser.parse_args()

	if args.xresources is None:
		def_xres = path.expanduser('~/.Xresources')
		def_xdft = path.expanduser('~/.Xdefaults')
		if path.isfile(def_xres):
			term_scheme = import_xresources(def_xres)
		elif path.isfile(def_xdft):
			term_scheme = import_xresources(def_xdft)
		else:
			term_scheme = DEFAULT_TERMINAL
	else:
		if path.isfile(args.xresources):
			term_scheme = import_xresources(args.xresources)
		else:
			term_scheme = DEFAULT_TERMINAL

	cparser = configparser.ConfigParser()
	if path.isfile(args.config_file):
		cparser.read(args.config_file)
	else:
		raise ValueError("Can't specify an empty config file!")
	print(cparser.sections())

