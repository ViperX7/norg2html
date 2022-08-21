"""
Code to export vim screen exactly to HTML
"""

import tkinter

import pyautogui as gui
import pyperclip

gui.hotkey("alt", "\t")
gui.typewrite("zR")
gui.typewrite(
    ":set nocursorcolumn nocursorline colorcolumn=10000 list! nornu! nonumber\n"
)
gui.typewrite(":IndentBlanklineToggle\n")


def snap_from_term():
    gui.hotkey("ctrl", "|")
    gui.hotkey("ctrl", "}")
    clipboard_content = pyperclip.paste()
    return clipboard_content


def get_term_output(ad_start=0, ad_end=None):
    buffer_dump = []

    old_clipboard_content = ""
    clipboard_content = "1"

    while (clipboard_content := snap_from_term()) != old_clipboard_content:
        # # Copy everything on screen gnome-terminal screen
        clipboard_content = clipboard_content.split("\n")
        clipboard_content = clipboard_content[1:-3][ad_start:ad_end]
        clipboard_content = "\n".join(clipboard_content)

        if old_clipboard_content == clipboard_content:
            return buffer_dump
        buffer_dump.append(clipboard_content)
        old_clipboard_content = clipboard_content
        gui.hotkey("pagedown")
        print("lc")
    print("X")


def squash_common(data: list):
    result = []
    for i, entry in enumerate(data):
        if i < (len(data) - 1):
            for lines in entry.split("\n"):
                print(lines)


squash_common(
    [
        "okokokok",
        "okokoktok",
        "tokokoktok",
    ]
)

bufcnt = get_term_output(0, -2)
bufcnt = "\n".join(bufcnt)
bufcnt = [
    "<pre>",
    "<center>",
    "<div style='background-color:#282C34;line-height:12pt'>",
    bufcnt,
    "</div>",
    "</center>",
    "</pre>",
]
bufcnt = "\n".join(bufcnt)
with open("test.md", "w") as file:
    file.write(bufcnt)

gui.hotkey("alt", "\t")
