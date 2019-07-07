from cudatext import *
import sys
import os
import shutil

INI = 'cuda_someformat.cfg'

def ini_global():
    ini = os.path.join(app_path(APP_DIR_SETTINGS), INI)
    ini0 = os.path.join(os.path.dirname(__file__), INI)
    if not os.path.isfile(ini) and os.path.isfile(ini0):
        shutil.copyfile(ini0, ini)
    return ini

def ini_local():
    fn = ed.get_filename()
    if fn:
        return os.path.join(os.path.dirname(fn), INI)
    else:
        return ''

def ini_filename():
    ini_g = ini_global()
    ini_l = ini_local()
    if os.path.isfile(ini_l):
        return ini_l
    else:
        return ini_g

def config_global():
    ini = ini_global()
    if os.path.isfile(ini):
        file_open(ini)
    else:
        msg_box('Global config file "%s" not found' % INI, MB_OK)

def config_local():
    if not ed.get_filename():
        msg_box('Cannot open local config file for untitled tab', MB_OK)
        return
    ini = ini_local()
    ini0 = ini_global()
    if os.path.isfile(ini):
        file_open(ini)
        return
    if not os.path.isfile(ini0):
        msg_box('Global config file "%s" not found' % INI, MB_OK)
        return
    if msg_box('Local config file "%s" not found.\nDo you want to create it?' % INI, MB_OKCANCEL)==ID_OK:
        shutil.copyfile(ini0, ini)
        if os.path.isfile(ini):
            file_open(ini)
        else:
            msg_box('Cannot copy global config file "%s" to local folder' % INI, MB_OK)


def run(do_format, msg):
    if ed.get_sel_mode() != SEL_NORMAL:
        msg_status(msg + "Column/line selections not supported")
        return

    text = ed.get_text_sel()
    if text:
        text = do_format(text)
        if not text:
            msg_status(msg + "Cannot format text")
            return

        msg_status(msg + "Formatted selection")

        x0, y0, x1, y1 = ed.get_carets()[0]
        if (y0, x0)>(y1, x1):
            x0, y0, x1, y1 = x1, y1, x0, y0

        ed.set_caret(x0, y0)
        ed.delete(x0, y0, x1, y1)
        ed.insert(x0, y0, text)
    else:
        text1 = ed.get_text_all()
        text = do_format(text1)
        if not text:
            msg_status(msg + "Cannot format text")
            return

        if text==text1:
            msg_status(msg + 'Text is already formatted')
            return

        msg_status(msg + "Formatted entire text")
        ed.set_caret(0, 0)
        ed.set_text_all(text)
