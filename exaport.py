"""
Code to export vim screen exactly to HTML
"""

import argparse
import subprocess
import tempfile
from os import remove
from shutil import copy

import pyautogui as gui
import pyperclip
from bs4 import BeautifulSoup


def inject_keybind():
    term_cfg = """
    [legacy/keybindings]
    copy-html='<Primary>braceright'
    select-all='<Primary>bar'
    """

    _, tmp = tempfile.mkstemp(".norg")
    with open(tmp, "w", encoding="utf-8") as file:
        file.write(term_cfg)

    kb_inject = f"cat {tmp} | dconf load /org/gnome/terminal/legacy/profiles:/"
    subprocess.run(kb_inject, shell=True, check=True)


def send_lines(keylist):
    """
    Press the supplied keys
    """
    if isinstance(keylist, str):
        gui.typewrite(keylist + "\n")
    elif isinstance(keylist, list):
        cmd = "\n".join(keylist)
        send_lines(cmd)
    else:
        raise TypeError()


def snap_from_term():
    """
    Copy's the text visible on the terminal screen
    """
    gui.hotkey("ctrl", "|")
    gui.hotkey("ctrl", "}")
    clipboard_content = pyperclip.paste()
    return clipboard_content


def find_match(slst):
    """
    Magic
    """
    slst = BeautifulSoup(slst, "lxml")
    slst = slst.text.split("\n")
    # __import__("pprint").pprint(slst)

    if slst[-1][0] == "~" and slst[-1].strip(" ") == "~":
        return True
    return False


def get_term_output(ad_start=0, ad_end=None):
    """
    Term output Processor for Neorg on nvim
    """
    buffer_dump = []

    old_clipboard_content = ""
    while (clipboard_content := snap_from_term()) != old_clipboard_content:

        old_clipboard_content = clipboard_content
        #  Copy everything on screen gnome-terminal screen
        clipboard_content = clipboard_content.split("\n")
        clipboard_content = clipboard_content[1:-3][ad_start:ad_end]
        clipboard_content = "\n".join(clipboard_content)

        buffer_dump.append(clipboard_content)
        gui.hotkey("pagedown")

    dmp = buffer_dump.pop() if find_match(buffer_dump[-2]) else None
    dmp = buffer_dump.pop() if find_match(buffer_dump[-2]) else None
    dmp = buffer_dump.pop() if find_match(buffer_dump[-2]) else dmp

    return buffer_dump


def post_processor(dump):
    """
    post processor
    """
    page = [
        "<pre>",
        "<center>",
        f"<font face='{FONT}'>"
        f"<div style='background-color:{BGCOLOR};line-height:12pt'>",
        dump,
        "</div>",
        "</font>",
        "</center>",
        "</pre>",
    ]
    page = "\n".join(page)
    return page


def export_norg(file_path, out_path=None):
    """
    Handler
    """
    out_path = out_path if out_path else file_path.replace("norg", "md")

    # Create a copy of original norg file
    copy(file_path, TMP_FILE_PATH)

    # Start the terminal
    if TERM_START_WIDTH:
        term_start_post = [
            f"stty columns {TERM_START_WIDTH}",
            f"nvim {TMP_FILE_PATH};exit",
        ]
        subprocess.run(TERM_START_RAW, check=True)
        send_lines(term_start_post)
    else:
        subprocess.run(TERM_START_CMD, check=True)
    gui.sleep(START_DELAY)

    # Conf Features
    vim_cmds = [
        ":set nocursorcolumn nocursorline colorcolumn=10000 list! norelativenumber nonumber",  # clean some clutter
        "zR",  # open all folds
        ":IndentBlanklineDisable",
    ]

    excmds = [":Neorg presenter start"]
    colcmds = [f":colorscheme {COLORSCHEME} "]
    vim_cmds = excmds + vim_cmds if ENABLE_PRESENTER else vim_cmds
    vim_cmds = colcmds + vim_cmds if COLORSCHEME else vim_cmds
    send_lines(vim_cmds)
    gui.sleep(PROCESS_DELAY)

    # post processing
    bufcnt = get_term_output() if ENABLE_PRESENTER else get_term_output(0, -2)
    if ENABLE_PRESENTER:
        pages = [post_processor(page) for page in bufcnt]
        document = "\n\n".join(pages)
    else:
        bufcnt = "\n".join(bufcnt)
        document = post_processor(bufcnt)

    with open(out_path, "w", encoding="utf-8") as file:
        file.write(document)

    exitcmdlst = [":qall!"]
    send_lines(exitcmdlst)
    remove(TMP_FILE_PATH)


_, TMP_FILE_PATH = tempfile.mkstemp(".norg")
TERM_START_CMD = ["gnome-terminal", "--", "nvim", TMP_FILE_PATH]
TERM_START_RAW = ["gnome-terminal"]
TERM_START_WIDTH = None

ENABLE_PRESENTER = False
START_DELAY = 1
PROCESS_DELAY = 1
BGCOLOR = "#282C34"
FONT = "Fira Code"
COLORSCHEME = None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--output", default=None, help="path to output")
    parser.add_argument("--font", default=FONT, help="font to set for the output")
    parser.add_argument("--bgcolor", default=BGCOLOR, help="background color to fill")
    parser.add_argument("--colorscheme", default=None, help="specify vim colorscheme")
    parser.add_argument(
        "--width", type=int, default=TERM_START_WIDTH, help="specify width"
    )
    parser.add_argument(
        "--presenter", action="store_true", help="Enable norg presenter mode"
    )
    args = parser.parse_args()
    inject_keybind()

    ENABLE_PRESENTER = args.presenter
    BGCOLOR = args.bgcolor
    FONT = args.font
    COLORSCHEME = args.colorscheme
    TERM_START_WIDTH = args.width

    export_norg(args.path, args.output)
