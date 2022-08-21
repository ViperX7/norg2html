"""
Code to export vim screen exactly to HTML
"""

import subprocess
import tempfile
from os import remove
from shutil import copy

import pyautogui as gui
import pyperclip


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


def get_term_output(ad_start=0, ad_end=None):
    """
    Term output Processor for Neorg on nvim
    """
    buffer_dump = []

    old_clipboard_content = ""
    while (clipboard_content := snap_from_term()) != old_clipboard_content:
        #  Copy everything on screen gnome-terminal screen
        clipboard_content = clipboard_content.split("\n")
        clipboard_content = clipboard_content[1:-3][ad_start:ad_end]
        clipboard_content = "\n".join(clipboard_content)

        if old_clipboard_content == clipboard_content:
            if buffer_dump[-1] == buffer_dump[-2]:
                buffer_dump.pop()
            elif CUT_FIX:
                buffer_dump.pop()
            break
        buffer_dump.append(clipboard_content)
        old_clipboard_content = clipboard_content
        gui.hotkey("pagedown")
    return buffer_dump


def export_norg():
    # Create a copy of original norg file
    copy(FILE_PATH, TMP_FILE_PATH)

    # Start the terminal
    out = subprocess.run(TERM_START_CMD, check=True)
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
    gui.sleep(START_DELAY)

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
    with open("test.md", "w") as file:
        file.write(bufcnt)

    cmdlst = [":qall!", "exit"]
    send_lines(cmdlst)
    remove(TMP_FILE_PATH)


BGCOLOR = "#282C34"
_, TMP_FILE_PATH = tempfile.mkstemp(".norg")
FILE_PATH = "../torch_1.norg"
TERM_START_CMD = ["gnome-terminal", "--", "nvim", TMP_FILE_PATH]
START_DELAY = 0.5
ENABLE_PRESENTER = True
CUT_FIX = not ENABLE_PRESENTER
FONT = "Fira Code"

KB_INJECT = "cat term.cfg | dconf load /org/gnome/terminal/legacy/profiles:/"
if __name__ == "__main__":
    export_norg()
