'''
Implements a UI for neovim  using tkinter.

* The widget has lines updated/deleted so that any
  given time it only contains what is being displayed.

* The widget is filled with spaces
'''
import os
import sys
import time
import math

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import WindowBase

from kyanvim.util import attach_headless, attach_child
from kyanvim.ui_bridge import UIBridge
from kyanvim.screen import Screen
from kyanvim import kv_util
from kyanvim.util import debug_echo, _stringify_key

RESIZE_DELAY = 0.04

def parse_tk_state(state):
    if state & 0x4:
        return 'Ctrl'
    elif state & 0x8:
        return 'Alt'
    elif state & 0x1:
        return 'Shift'


KV_MODS = ('lctrl', 'rctrl',
           'alt', 'alt-gr',
           'shift', 'rshift',
           'super')


KEY_TABLE = {
    'escape': 'Esc',
    # 'tab': 'Tab' # TODO
    # 'slash': '/',
    # 'backslash': '\\',
    # 'asciicircumf': '^',
    # 'at': '@',
    # 'numbersign': '#',
    # 'dollar': '$',
    # 'percent': '%',
    # 'ampersand': '&',
    # 'asterisk': '*',
    # 'parenleft': '(',
    # 'parenright': ')',
    # 'underscore': '_',
    # 'plus': '+',
    # 'minus': '-',
    # 'bracketleft': '[',
    # 'bracketright': ']',
    # 'braceleft': '{',
    # 'braceright': '}',
    # 'quotedbl': '"',
    # 'apostrophe': "'",
    # 'less': "<",
    # 'greater': ">",
    # 'comma': ",",
    # 'period': ".",
    # 'BackSpace': 'BS',
    # 'Return': 'CR',
    # 'Delete': 'Del',
    # 'Next': 'PageUp',
    # 'Prior': 'PageDown',
    # 'Enter': 'CR',
}

ITEMS = {}

class MixTk():
    '''
    Tkinter actions we bind and use to communicate to neovim
    '''
    @staticmethod
    def is_uppercaseable(char):
        if char == char.upper():
            return False
        return True

    def _kv_key_pressed(self, kb, keycode, text, modifiers):
        assert text != ''
        assert len(modifiers) < 2

        print(text, chr(keycode[0]), keycode[0], keycode[1], modifiers)
        # Single or multi key mod pressed (without a key)
        if keycode[1] in KV_MODS:
            # print('MOD PRESESD GTFO')
            return True
        elif modifiers == ['shift']:
            if self.is_uppercaseable(text):
                # print('SENDING UPPER CASE', text.upper())
                self._bridge.input(text.upper())
                return True
        elif text != None and not modifiers:
            # Normal key
            # print('SEND NORMAL KEY', text)
            self._bridge.input(text)
            return True
        # print('TRANSLATE FOR VIM..')
        # Translate special key so vim understands (with or without mods)
        try:
            state = modifiers[0]
        except IndexError:
            state = None
        input_str = _stringify_key(KEY_TABLE.get(keycode[1], keycode[1]), state)
        self._bridge.input(input_str)
        # If an escape was pressed we must refocus ourselves fml kivy
        #TODO failing
        if keycode[0] == 27:
            self.widget.focus = True
        return True

    def _tk_quit(self, *args):
        self._bridge.exit()

    # @rate_limited(1/RESIZE_DELAY, mode='kill')
    def _tk_resize(self, event):
        '''Let Neovim know we are changing size'''
        cols = int(math.floor(event.width / self._colsize))
        rows = int(math.floor(event.height / self._rowsize))
        if self._screen.columns == cols:
            if self._screen.rows == rows:
                return
        self.current_cols = cols
        self.current_rows = rows
        self._bridge.resize(cols, rows)
        if self.debug_echo:
            print('resizing c, r, w, h',
                    cols,rows, event.width, event.height)


    def bind_resize(self):
        '''
        after calling,
        widget changes will now be passed along to neovim
        '''
        # print('binding resize to', self, self.canvas)
        self._configure_id = self.canvas.bind('<Configure>', self._tk_resize)


    def unbind_resize(self):
        '''
        after calling,
        widget size changes will not be passed along to nvim
        '''
        # print('unbinding resize from', self)
        self.canvas.unbind('<Configure>', self._configure_id)


class NvimHandler(MixTk):
    '''These methods get called by neovim'''

    def __init__(self, widget, toplevel, address=-1, debug_echo=False):
        self.widget = widget
        self.toplevel = toplevel
        self.debug_echo = debug_echo

        self._insert_cursor = False
        self._screen = None
        self._colsize = None
        self._rowsize = None

        # Have we connected to an nvim instance?
        self.connected = False
        # Connecition Info for neovim
        self.address = address
        cols = 80
        rows = 24
        self.current_cols = cols
        self.current_rows = rows

        self._screen = Screen(cols, rows)
        self._bridge = UIBridge()

        # The negative number makes it pixels instead of point sizes
        # size = self.canvas.make_font_size(13)
        # self._fnormal = tkfont.Font(family='Monospace', size=size)
        # self._fbold = tkfont.Font(family='Monospace', weight='bold', size=size)
        # self._fitalic = tkfont.Font(family='Monospace', slant='italic', size=size)
        # self._fbolditalic = tkfont.Font(family='Monospace', weight='bold',
                                 # slant='italic', size=size)
        # self.canvas.config(font=self._fnormal)
        # self._colsize = self._fnormal.measure('M')
        # self._rowsize = self._fnormal.metrics('linespace')
        self._colsize = 15
        self._rowsize = 15

    @debug_echo
    def connect(self, *nvim_args, address=None, headless=True, exec_name='nvim'):
        # Value has been set, otherwise default to this functions default value
        if self.address != -1 and not address:
            address = self.address

        if headless:
            nvim = attach_headless(nvim_args, address)
        elif address:
            nvim = attach('socket', path=address, argv=nvim_args)
        else:
            nvim = attach_child(nvim_args=nvim_args, exec_name=exec_name)

        self._bridge.connect(nvim, self.widget)
        self._screen = Screen(self.current_cols, self.current_rows)
        self._bridge.attach(self.current_cols, self.current_rows, rgb=True)
        # if len(sys.argv) > 1:
            # nvim.command('edit ' + sys.argv[1])
        self.connected = True
        self.widget.nvim = nvim
        return nvim

    @debug_echo
    def _nvim_resize(self, cols, rows):
        '''Let neovim update tkinter when neovim changes size'''
        # TODO
        # Make sure it works when user changes font,
        # only can support mono font i think..
        # self._screen = Screen(cols, rows)
        self._screen.resize(cols, rows)
        top, left, bot, right = 0, 0, rows-1, cols-1
        self.widget._destroy_cells(top, bot, left, right)
        self.widget._create_cells(top, left, bot, right,
                                  self._rowsize, self._colsize)

    # @debug_echo
    def _nvim_clear(self):
        '''
        wipe everyything, even the ~ and status bar
        '''
        self._screen.clear()

    # @debug_echo
    def _nvim_eol_clear(self):
        '''
        clear from cursor position to the end of the line
        '''
        self._screen.eol_clear()

    # @debug_echo
    def _nvim_cursor_goto(self, row, col):
        '''Move gui cursor to position'''
        self._screen.cursor_goto(row, col)

    # @debug_echo
    def _nvim_busy_start(self):
        self._busy = True

    def _nvim_busy_stop(self):
        self._busy = False

    def _nvim_mouse_on(self):
        self.mouse_enabled = True

    def _nvim_mouse_off(self):
        self.mouse_enabled = False

    # @debug_echo
    def _nvim_mode_change(self, mode):
        self._insert_cursor = mode == 'insert'

    # @debug_echo
    def _nvim_set_scroll_region(self, top, bot, left, right):
        self._screen.set_scroll_region(top, bot, left, right)

    # @debug_echo
    def _nvim_scroll(self, count):
        self._screen.scroll(count)

    # @debug_echo
    def _nvim_highlight_set(self, attrs):
        self._screen.attrs.set_next(attrs)

    # @debug_echo
    def _nvim_put(self, text):
        '''
        put a charachter into position, we only write the lines
        when a new row is being edited
        '''
        self._screen.put(text)

    def _nvim_bell(self):
        pass

    def _nvim_visual_bell(self):
        pass

    # @debug_echo
    def _nvim_update_fg(self, fg):
        self._screen.attrs.set_default('foreground', fg)

    # @debug_echo
    def _nvim_update_bg(self, bg):
        self._screen.attrs.set_default('background', bg)

    # @debug_echo
    def _nvim_update_sp(self, sp):
        self._screen.attrs.set_default('special', sp)

    # @debug_echo
    def _nvim_update_suspend(self, arg):
        self.root.iconify()

    # @debug_echo
    def _nvim_set_title(self, title):
        self.root.title(title)

    # @debug_echo
    def _nvim_set_icon(self, icon):
        pass
        # self._icon = tk.PhotoImage(file=icon)
        # self.root.tk.call('wm', 'iconphoto', self.root._w, self._icon)

    # @debug_echo
    def _flush(self):
        if self._screen._dirty.is_dirty():
            top, left, bot, right = self._screen._dirty.get()
            # print('reparing ', '%s.%s' % (top, left), '%s.%s' % (bot, right))
            # print('max ', '%s.%s' % (self._screen.top, self._screen.left), '%s.%s' % (self._screen.bot, self._screen.right))
            for row, col, text, attrs in self._screen.iter(
                                        top, bot, left, right) :
                self._draw(row, col, text, attrs)
                # print(row, col, text, attrs)
            self._screen._dirty.reset()


    # @debug_echo
    def _draw(self, row, col, data, attrs):
        '''
        updates a line :) from row,col to eol using attrs
        '''
        end = col + len(data)
        # font = self._fnormal
        fg = attrs[0]['foreground']
        bg = attrs[0]['background']
        for i, c in enumerate(range(col, end)):
            self.widget._update_cell(row, c, data[i], 13, fg, bg, self._screen.bot)


    @debug_echo
    def _nvim_exit(self, arg):
        print('in exit')
        import pdb;pdb.set_trace()
        # self.root.destroy()

class KyanVimEditor(kv_util.KvCanvas):
    '''namespace for neovim related methods,
    requests are generally prefixed with _tk_,
    responses are prefixed with _nvim_
    '''
    # we get keys, mouse movements inside tkinter, using binds,
    # These binds are handed off to neovim using _input

    # Neovim interpruts the actions and calls certain
    # functions which are defined and implemented in tk

    # The api from neovim does stuff line by line,
    # so each callback from neovim produces a series
    # of miniscule actions which in the end updates a line

    # So we can shutdown the neovim connections
    instances = []

    def __init__(self, *_, address=False, toplevel=False, **kwargs):
        '''
        :parent: normal kivy parent or master of the widget
        :toplevel: , if true will resize based off the toplevel etc
        :address: neovim connection info
            named pipe /tmp/nvim/1231
            tcp/ip socket 127.0.0.1:4444
            'child'
            'headless'
        :kwargs: config options for text widget
        '''
        kv_util.KvCanvas.__init__(self, **kwargs)
        self.nvim_handler = NvimHandler(widget=self,
                                        toplevel=toplevel,
                                        address=address,
                                        debug_echo=True)

        # TODO weak ref?
        KyanVimEditor.instances.append(self)

    def _nvimkv_config(self, *args):
        '''required config'''
        pass
        # Hide tkinter cursor
        # self.config(insertontime=0)

        # Remove Default Bindings and what happens on insert etc
        # bindtags = list(self.bindtags())
        # bindtags.remove("Canvas")
        # self.bindtags(tuple(bindtags))

        self.keyboard_on_key_down = self.nvim_handler._kv_key_pressed
        # self.bind('<Key>', self.nvim_handler._kv_key_pressed)

        # self.bind('<Button-1>', lambda e: self.focus_set())

    def nvim_connect(self, *a, **k):
        ''' force connection to neovim '''
        self.nvim_handler.connect(*a, **k)
        self._nvimkv_config()

    def schedule_screen_update(self, apply_updates):
        '''This function is called from the bridge,
           apply_updates calls the required nvim actions'''
        def do(_):
            if self.nvim_handler.debug_echo:
                print()
                print('Begin')
            apply_updates()
            self.nvim_handler._flush()
            if self.nvim_handler.debug_echo:
                print('End')
                print()
            # self.nvim_handler._start_blinking()
        Clock.schedule_once(do, 0)


    def quit(self):
        print('do quit..')
        # Clock.schedule_once(self.app.quit, 1)
        # self.root.after_idle(self.root.quit)

if __name__ == '__main__':
    from kyanvim.example import ExampleApp
    app = ExampleApp()
    app.run()
