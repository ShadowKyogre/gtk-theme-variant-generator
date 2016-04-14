from argparse import ArgumentParser
import configparser
from copy import deepcopy
from os import path, makedirs
import re
import sys
import shutil

XRESOURCE=re.compile(r'^\*\.(foreground|background|cursorColor|color\d+):\s*(\S+)', re.MULTILINE)

SPECIAL_SECTIONS = {'HINTS_GTK2', 'HINTS_GTK3'}

INDEXTHEME_REPL=re.compile('^(Name|GtkTheme|MetacityTheme)=(.*)$', re.MULTILINE)

REPL_KEY_FORMAT=r'\b{0}\b'

HEXADECIMAL_COLORS=re.compile('#([a-f0-9]{3}|[a-f0-9]{6})', re.IGNORECASE)

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

global NOISY
NOISY=False

def import_xresources(fpath):
	output = deepcopy(DEFAULT_TERMINAL)
	with open(fpath, 'r', encoding='utf-8') as f:
		textctnt = f.read()
		for k, v in XRESOURCE.findall(textctnt):
			output[k]=v
	return output

def update_theme_metadata(theme_dir, variant, fmt):
	idx_theme = path.join(theme_dir, 'index.theme')
	with open(idx_theme, 'r', encoding='utf-8') as f:
		fcontents = f.read()

	fcontents = INDEXTHEME_REPL.sub(r'\1={0}'.format(fmt.format(variant)), fcontents)

	with open(idx_theme, 'w', encoding='utf-8') as f:
		f.write(fcontents)

def update_theme_colors(subfile, variant_colors, term_scheme):
	global NOISY
	with open(subfile, 'r', encoding='utf-8') as f:
		fcontents = f.read()

	for colname, color in variant_colors:
		if not HEXADECIMAL_COLORS.match(color):
			true_color = term_scheme[color]
		else:
			true_color = color
		if NOISY:
			if true_color != color:
				print("--", colname, "->", color, "->", true_color)
			else:
				print("--", colname, "->", true_color)
		fcontents = re.sub(REPL_KEY_FORMAT.format(colname), true_color, fcontents)

	with open(subfile, 'w', encoding='utf-8') as f:
		f.write(fcontents)

if __name__ == "__main__":
	aparser = ArgumentParser()
	aparser.add_argument('--xresources', '-x',
	                     default=None,
	                     help='Read colors from an xrdb file')
	aparser.add_argument('--dir-format', '-f',
	                     default='{0}{1}',
	                     help='Directory name format for variants')
	aparser.add_argument('--readable-format', '-r',
	                     default=r'{0}\2',
	                     help='Readable name format for variants')
	aparser.add_argument('--config-file',  '-c',
	                     default=path.join(path.dirname(__file__), 'variants.conf'),
	                     help='Look for replacement hints and variants with the alternate config file')
	aparser.add_argument('--input-dir',  '-i',
	                     default=path.join(path.dirname(__file__), 'templates'),
	                     help='Input directory for themes to make variants of')
	aparser.add_argument('--output-dir', '-o',
	                     default=path.join(path.dirname(__file__), 'output'),
	                     help='Output directory for variants')
	aparser.add_argument('--verbose', '-v', default=False, action='store_true',
	                     help='Be verbose about the creation of the variants')
	args = aparser.parse_args()

	if args.xresources is None:
		def_xdft = path.expanduser('~/.Xdefaults')
		if path.isfile(def_xdft):
			if args.verbose:
				print('Reading X defaults for your terminal color scheme')
			term_scheme = import_xresources(def_xdft)
		else:
			if args.verbose:
				print('Using fallback terminal color scheme')
			term_scheme = DEFAULT_TERMINAL
	else:
		if path.isfile(args.xresources):
			if args.verbose:
				print('Reading Xrdb file {0} for your terminal color scheme'.format(repr(args.xresources)))
			term_scheme = import_xresources(args.xresources)
		else:
			if args.verbose:
				print('Using fallback terminal color scheme')
			term_scheme = DEFAULT_TERMINAL
	
	NOISY=args.verbose

	cparser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
	cparser.optionxform = lambda option: option
	if path.isfile(args.config_file):
		cparser.read(args.config_file)
	else:
		raise ValueError("Can't specify an empty config file!")

	if not cparser.has_section('HINTS_GTK3') and not cparser.has_section('HINTS_GTK2'):
		raise ValueError("No hints for where the colors are!")
	else:
		themes_total = set(cparser.options('HINTS_GTK3')+cparser.options('HINTS_GTK2'))
		variants = set(cparser.sections()) - SPECIAL_SECTIONS
		if path.exists(args.output_dir):
			raise ValueError("Output dir exists, not going to go there!")

		if NOISY:
			print("Making variants for:", ', '.join(themes_total))

		for theme in themes_total:
			for variant in variants:
				if NOISY:
					print("Making variant", args.readable_format.replace(r'\2', '{1}').format(variant, theme))
				#dummycpy = path.join(args.output_dir, theme)
				odir = path.join(args.output_dir, args.dir_format.format(variant, theme))
				idir = path.join(args.input_dir, theme)
				if NOISY:
					print("- Copying template to:", odir)
				shutil.copytree(idir, odir)
				#shutil.move(dummycpy, odir)
				update_theme_metadata(odir, variant, args.readable_format)
				variant_colors = cparser.items(variant)

				if cparser.has_option('HINTS_GTK3', theme) and path.isdir(path.join(odir, 'gtk-3.0')):
					if NOISY:
						print("- Writing GTK3 theme colors")
					subfile = cparser.get('HINTS_GTK3', theme)
					update_theme_colors(path.join(odir, 'gtk-3.0', subfile), variant_colors, term_scheme)

				if cparser.has_option('HINTS_GTK2', theme) and path.isdir(path.join(odir, 'gtk-2.0')):
					if NOISY:
						print("- Writing GTK2 theme colors")
					subfile = cparser.get('HINTS_GTK2', theme)
					update_theme_colors(path.join(odir, 'gtk-2.0', subfile), variant_colors, term_scheme)
