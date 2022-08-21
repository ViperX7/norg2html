# Installation

## Dump this into your terminal

```sh
git clone https://github.com/viperx7/norg2html
cd norg2html
pip3 install -r requirements.txt
mv norg2html.py ~/.local/bin/norg2html
chomd +x ~/.local/bin/norg2html
cd ..
rm norg2html -r
```



## Requirements

1. **Gnome Terminal**  : _No other terminal would work_
2. **stty**            : _This should be already there_



# Usage

```term
usage: norg2html [-h] [--output OUTPUT] [--font FONT] [--bgcolor BGCOLOR]
                    [--colorscheme COLORSCHEME] [--width WIDTH] [--presenter]
                    path

positional arguments:
  path

options:
  -h, --help                 show this help message and exit
  --output OUTPUT            path to output
  --font FONT                font to set for the output
  --bgcolor BGCOLOR          background color to fill
  --colorscheme COLORSCHEME  specify vim colorscheme
  --width WIDTH              specify width
  --presenter                Enable norg presenter mode</pre>
```



## Example


```sh
norg2html ./README.norg --width 100
```
