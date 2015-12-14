# GTK Theme Variant Generator

## What is this?
This is a theme generator that makes themes based on the template themes you
put in it. Currently, there's two themes that I have here that are
variant-ready:
- cathexis theme (Not mine, from dA)
- TrueDark theme (gtk-2.0 version originated from Dust TrueDark, gtk-3.0 version hand-coded)

Variants are specified in a config file like the one found in here. There are
two special sections: HINTS_GTK3 and HINTS_GTK2. These tell the script what
file to look for the colors in.

The rest of the sections specify variants. Names for the colors can be
anything. Just make sure your template has the same name for it to be properly
replaced. Color values can be hexadecimal or special color names like color1,
color 15, etc. to sync with your terminal color scheme.

## Caveats
- Haven't figured out how to get python to ignore the fact that the root of the
  output dir exists, but not the last part of it.
- Suggesting themes from images'd be nice.
- No autoreload.
