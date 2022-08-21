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


def export_norg(file_path, out_path=None):
    """
    Handler
    """
    out_path = out_path if out_path else file_path.replace("norg", "md")

    # Create a copy of original norg file
    copy(file_path, TMP_FILE_PATH)

    # Start the terminal
    subprocess.run(TERM_START_CMD, check=True)
    gui.sleep(START_DELAY)

    # Conf Features
    vim_cmds = [
        ":set nocursorcolumn nocursorline colorcolumn=10000 list! norelativenumber nonumber",  # clean some clutter
        "zR",  # open all folds
        ":IndentBlanklineDisable",
    ]

    excmds = [":Neorg presenter start"]
    vim_cmds = excmds + vim_cmds if ENABLE_PRESENTER else vim_cmds
    send_lines(vim_cmds)
    gui.sleep(PROCESS_DELAY)

    # post processing
    bufcnt = get_term_output() if ENABLE_PRESENTER else get_term_output(0, -2)
    bufcnt = "\n".join(bufcnt)
    bufcnt = [
        "<pre>",
        "<center>",
        f"<font face='{FONT}'>"
        f"<div style='background-color:{BGCOLOR};line-height:12pt'>",
        bufcnt,
        "</div>",
        "</font>",
        "</center>",
        "</pre>",
    ]
    bufcnt = "\n".join(bufcnt)
    print(out_path)
    with open(out_path, "w", encoding="utf-8") as file:
        file.write(bufcnt)

    cmdlst = [":qall!", "exit"]
    send_lines(cmdlst)
    remove(TMP_FILE_PATH)


_, TMP_FILE_PATH = tempfile.mkstemp(".norg")
TERM_START_CMD = ["gnome-terminal", "--", "nvim", TMP_FILE_PATH]
KB_INJECT = "cat term.cfg | dconf load /org/gnome/terminal/legacy/profiles:/"

ENABLE_PRESENTER = False
START_DELAY = 1
PROCESS_DELAY = 1
BGCOLOR = "#282C34"
FONT = "Fira Code"
COLORSCHEME = None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--font", default=FONT, help="font to set for the output")
    parser.add_argument("--bgcolor", default=BGCOLOR, help="background color to fill")
    parser.add_argument("--colorscheme", default=None, help="specify vim colorscheme")
    parser.add_argument("--presenter", default=False, help="Enable norg presenter mode")
    args = parser.parse_args()

    ENABLE_PRESENTER = args.presenter
    BGCOLOR = args.bgcolor
    FONT = args.font
    COLORSCHEME = args.colorscheme

    export_norg(args.path)
