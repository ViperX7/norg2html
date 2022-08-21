"""
Code to export vim screen exactly to HTML
"""

import subprocess

import pyautogui as gui
import pyperclip


def send_lines(keylist):
    """
    Press the supplied
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
            buffer_dump.pop()
            break
        buffer_dump.append(clipboard_content)
        old_clipboard_content = clipboard_content
        gui.hotkey("pagedown")
    return buffer_dump


# def squash_common(data: list):
#     result = []
#     for i, entry in enumerate(data):
#         if i < (len(data) - 1):
#             for lines in entry.split("\n"):
# print(lines)

# Configurables
BGCOLOR = "#282C34"
FILE_PATH = "../torch_1.norg"
TERM_START_CMD = ["gnome-terminal", "--", "nvim", FILE_PATH]
START_DELAY = 1

# Start the terminal
out = subprocess.run(TERM_START_CMD, check=True)
gui.sleep(START_DELAY)

# Conf Features
vim_cmds = [
    ":set nocursorcolumn nocursorline colorcolumn=10000 list! nornu! nonumber",
    ":IndentBlanklineToggle",
    "zR",
]

send_lines(vim_cmds)
gui.sleep(START_DELAY)

# post processing
bufcnt = get_term_output(0, -2)
bufcnt = "\n".join(bufcnt)
bufcnt = [
    "<pre>",
    "<center>",
    f"<div style='background-color:{BGCOLOR};line-height:12pt'>",
    bufcnt,
    "</div>",
    "</center>",
    "</pre>",
]
bufcnt = "\n".join(bufcnt)
with open("test.md", "w") as file:
    file.write(bufcnt)

cmdlst = [":qall!", "exit"]
send_lines(cmdlst)
