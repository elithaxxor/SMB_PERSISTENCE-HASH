#!/usr/bin/env python3
import curses
import subprocess

## SHOOTS EVERYTHING OFF AT ONCE 

def run_script(script_path):
    try:
        subprocess.run(["python3", script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}: {e}")

def run_all_scripts(scripts):
    for script in scripts:
        run_script(script)

def main_menu(stdscr, scripts):
    curses.curs_set(0)
    current_row = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        menu_items = ["Run All Tools"] + scripts + ["Exit"]
        for idx, row in enumerate(menu_items):
            x = width//2 - len(row)//2
            y = height//2 - len(menu_items)//2 + idx
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, row)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, row)

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == 0:
                run_all_scripts(scripts)
            elif current_row == len(menu_items) - 1:
                break
            else:
                run_script(scripts[current_row - 1])

            stdscr.clear()
            stdscr.addstr(0, 0, "Press any key to return to the menu")
            stdscr.refresh()
            stdscr.getch()

def main():
    scripts = [
        "SMB_ENUM/python/tool/smb_enum.py",
        "SMB_ENUM/python/tool/smb_enum_II.py"
    ]

    curses.wrapper(main_menu, scripts)

if __name__ == "__main__":
    curses.wrapper(main)
