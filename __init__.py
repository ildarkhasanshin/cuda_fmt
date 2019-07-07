import os
import importlib
import cudatext as app
import json
from cudatext import ed
from . import format_proc

MAX_SECTIONS = 10
FN_CFG = os.path.join(app.app_path(app.APP_DIR_SETTINGS), 'cuda_fmt.json')

class Command:
    helpers = {}
    helpers_plain = []

    def __init__(self):

        dir = app.app_path(app.APP_DIR_PY)
        dirs = os.listdir(dir)
        dirs = [os.path.join(dir, s) for s in dirs if s.startswith('cuda_fmt_')]

        for dir in dirs:
            fn_inf = os.path.join(dir, 'install.inf')
            s_module = app.ini_read(fn_inf, 'info', 'subdir', '')
            for index in range(1, MAX_SECTIONS+1):
                section = 'fmt'+str(index)
                s_method = app.ini_read(fn_inf, section, 'method', '')
                if not s_method: continue
                s_lexers = app.ini_read(fn_inf, section, 'lexers', '')
                if not s_lexers: continue
                s_caption = app.ini_read(fn_inf, section, 'caption', '')
                if not s_caption: continue
                s_config = app.ini_read(fn_inf, section, 'config', '')
                force_all = app.ini_read(fn_inf, section, 'force_all', '')=='1'

                helper = {
                        'module': s_module,
                        'method': s_method,
                        'lexers': s_lexers,
                        'caption': s_caption,
                        'config': s_config,
                        'force_all': force_all,
                        }

                self.helpers_plain.append(helper)

                for s_lex in s_lexers.split(','):
                    if s_lex not in self.helpers:
                        self.helpers[s_lex] = [helper]
                    else:
                        self.helpers[s_lex].append(helper)

        items = sorted(list(self.helpers.keys()))
        if items:
            print('Formatters: ' + ', '.join(items))

        self.load_labels()


    def load_labels(self):

        if not os.path.isfile(FN_CFG):
            return

        for helper in self.helpers_plain:
            helper['label'] = None

        with open(FN_CFG, 'r', encoding='utf8') as f:
            data = json.load(f)
            for key in data:
                val = data[key]
                for helper in self.helpers_plain:
                    if helper['caption'] == key:
                        helper['label'] = val
                        #print(helper)
                        continue


    def get_func(self, lexer):

        d = self.helpers.get(lexer)
        if not d: return

        if len(d)==1:
            item = d[0]
        else:
            items = [item['caption'] for item in d]
            res = app.dlg_menu(app.MENU_LIST, items, caption='Formatters for %s'%lexer)
            if res is None: return False
            item = d[res]

        module = item['module']
        method = item['method']
        caption = item['caption']
        force_all = item['force_all']

        _m = importlib.import_module(module)
        func = getattr(_m, method)
        return (func, caption, force_all)


    def format(self):

        lexer = ed.get_prop(app.PROP_LEXER_FILE)
        if not lexer:
            app.msg_status('No formatters for None-lexer')
            return

        res = self.get_func(lexer)
        if res is None:
            app.msg_status('No formatters for "%s"'%lexer)
            return

        if res==False:
            return

        func, caption, force_all = res
        format_proc.run(func, '['+caption+'] ', force_all)


    def config(self, is_global):

        items = [item for item in self.helpers_plain if item['config']]
        if not items:
            app.msg_status('No configurable formatters')
            return

        caps = ['%s (%s)\t%s'%(item['caption'], item['config'], item['lexers']) for item in items]

        res = app.dlg_menu(app.MENU_LIST_ALT, caps, caption='Formatters')
        if res is None: return
        item = items[res]

        ini = item['config']
        if is_global:
            format_proc.config_global(ini)
        else:
            format_proc.config_local(ini)

    def config_global(self):

        self.config(True)

    def config_local(self):

        self.config(False)

    def config_labels(self):

        pass

    def format_label(self, label):

        lexer = ed.get_prop(app.PROP_LEXER_FILE)
        if not lexer:
            return

        helpers = self.helpers.get(lexer)
        if not helpers:
            app.msg_status('No formatters for "%s"'%lexer)
            return

        for helper in helpers:
            if helper['label']==label:
                _m = importlib.import_module(helper['module'])
                func = getattr(_m, helper['method'])
                format_proc.run(
                    func,
                    '['+helper['caption']+'] ',
                    helper['force_all']
                    )
                return

        app.msg_status('No formatter for "%s" with label "%s"'%(lexer, label))


    def format_a(self):

        self.format_label('A')

    def format_b(self):

        self.format_label('B')

    def format_c(self):

        self.format_label('C')

    def format_d(self):

        self.format_label('D')
