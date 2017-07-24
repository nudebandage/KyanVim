# TODO
# Nested data instead of nested Classes

from random import random as rnd
from random import choice

from kivy.graphics.texture import Texture
from kivy.cache import Cache
from kivy.clock import Clock
from kivy.graphics import Canvas as BaseCanvas
from kivy.graphics import Color, Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.uix.widget import Widget as BaseWidget
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex

from kyanvim.screen import Screen
from kyanvim.util import timerfunc

Cache_register = Cache.register
Cache_append = Cache.append
Cache_get = Cache.get
Cache_remove = Cache.remove
Cache_register('textinput.label', timeout=120.)
# Cache_register('textinput.width', timeout=60.)

global a, b, c

def apply(func, iter):
    for i in iter:
        func(i)

class KvCell(BaseWidget):
    '''A cell containg a bg and text'''
    def __init__(self, row, col, width, height, bg, fg):
        super().__init__()
        self.bg = bg
        self.fg = fg
        self.pos = (col*width, row*height)
        self.size = (width, height)
        with self.canvas:
            # Draw the background
            self.k_bg_col = Color(*self.bg, mode='rgba')
            self.k_bg_rect = Rectangle(pos=self.pos, size=self.size)
            self.k_fg_col = Color(*fg, mode='rgba')
            texture = self._create_texture('', {'font_size':13})
            self.k_fg_rect = Rectangle(pos=self.pos)
            self.k_fg_rect.texture = texture
            self.k_fg_rect.size=texture.size

    def _create_texture(self, text:str, attrs:dict):
        ''' Create a label from a text, using line options, CACHED'''
        assert len(text) == 1 or text == ''

        cid = '%s\0%s' % (text, str(attrs))
        texture = Cache_get('textinput.label', cid)
        if texture is None:
            # if text == '\n':
                # texture = Texture.create(size=(1, 1))
            # else:
            label = CoreLabel(text=text, **attrs)
            label.refresh()
            texture = label.texture
            Cache_append('textinput.label', cid, texture)
        return texture

    def update(self, text='', fg=None, bg=None, pos=None, size=None):
        '''Update the cells values'''
        # Delete the canvas instructions of this cell
        bg = self.bg if not bg else bg
        fg = self.fg if not fg else fg
        pos = self.pos if not pos else pos
        size = self.size if not size else size

        attrs = {'font_size':13}

        with self.canvas:
            texture = self._create_texture(text, attrs)
            self.k_bg_col.rgba = bg
            self.k_fg_col.rgba = fg
            self.k_bg_rect.pos = pos
            self.k_fg_rect.pos = pos
            self.k_fg_rect.texture = texture
            self.k_fg_rect.size = texture.size

    def scroll(self, y:int, p=False):
        orig = self.pos[1]
        self.pos = (self.pos[0], self.pos[1] + y)
        if p:
            print(orig, self.pos[1])
        self.k_bg_rect.pos = self.pos
        self.k_fg_rect.pos = self.pos
        global a, b, c
        # self.k_bg_col.rgba = (a, b, c, 1)
        # self.k_fg_col.rgba = (a, b, c, 1)


class _Canvas(BaseCanvas):
    '''Canvas used by our Widget'''
    def create_cell(self, row, col, width, height, bg, fg):
        '''create a blank cell at the correct position'''
        return KvCell(row, col, width, height, bg, fg)

    def update_cell_text(self, kvcell:KvCell, data, fg, bg):
        '''Update a cells contents'''
        kvcell.update(data, fg=fg, bg=bg)

    def update_cell_pos(self, kvcell, pos):
        kvcell.update(pos=pos)
        pass


# NOT NEEEDED
class _Widget(BaseWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas = _Canvas()


#TODO RENAME - > KivyNvim
class BASE:
    def _clear(self):
        self._screen.clear()

    def _eol_clear(self):
        self._screen.eol_clear()

    def _cursor_goto(self, row, col):
        self._screen.cursor_goto(row, col)

    def _set_scroll_region(self, top, bot, left, right):
        self._screen.set_scroll_region(top, bot, left, right)

    def _set_attrs_next(self, attrs):
        self._screen.attrs.set_next(attrs)

    def _put(self, text):
        self._screen.put(text)

    def _update_fg(self, fg):
        self._screen.attrs.set_default('foreground', fg)

    def _update_bg(self, bg):
        self._screen.attrs.set_default('background', bg)

    def _update_sp(self, sp):
        self._screen.attrs.set_default('special', sp)

    def _resize(self, columns, rows, rowsize, colsize):
        '''destory all cells and reinit the screen to columns and rows'''
        self._screen.resize(columns, rows)
        self.canvas.clear()

        top, left, bot, right = 0, 0, rows-1, columns-1
        # add cells, kivy 0,0 is bottom left'''
        # print('CREATE CELLS', top, left, bot, right)
        attrs = self._screen.attrs.ui_cache.get(None)[0]
        bg = attrs['background']
        fg = attrs['foreground']

        # for row in range(top, bot + 1):
            # for col in range(left, right + 1):
                # kivy 0 is at bottom of screen, invert it with bot-row
                # cell = self._screen.get_cell(row, col)
                # kv_row = bot - row
                # kvcell = self._canvas.create_cell(kv_row, col, colsize, rowsize, bg, fg)
                # cell.set_canvas_data(kvcell)
                # self.add_widget(kvcell)


    def _update_cell(self, kvcell:KvCell, data:str, fg, bg):
        self.canvas.update_cell_text(kvcell, data, fg=fg, bg=bg)

    def _scroll_cells(self, count, rowsize):
        # top, bot = self._screen.top, self._screen.bot
        # left, right = self._screen.left, self._screen.right

        # if count > 0:
            # move_top, move_bot = top + count, bot - count + 1
        # else:
            # move_top, move_bot = top, bot + count

        # The following two commands only operate on the UI cells
        # Scroll the widget cells
        # apply(lambda cell: cell.get_canvas_data().scroll(count*rowsize),
              # self._screen.iter(move_top, left, move_bot, right))

        self._screen.scroll(count)

    def _update_cell_range(self, row, col, data:str, fg, bg):
        for i, cell in enumerate(self._screen.iter(row, col, row, col -1 + len(data))):

            self._update_cell(cell.get_canvas_data(), data[i], fg, bg)

    def update_line(self, row, col, substring, attrs):
        text = self._lines[row]
        new_text = text[:col] + substring + text[col:]
        self._set_line_text(row, new_text)


class KvCanvas(FocusBehavior, BASE, _Widget):
    def __init__(self, columns, rows, *_, **kwargs):
        super().__init__(**kwargs)
        self._screen = Screen(columns, rows)


class KvFull(TextInput, BASE):
    """
    At the moment just implement the full Textinput
    We repaint the entire screen.
    """
    def __init__(self, columns, rows, *_, **kwargs):
        TextInput.__init__(self, **kwargs)
        self._screen = Screen(columns, rows)
        # import pdb;pdb.set_trace()
        # self._update_graphics_ev = Clock.create_trigger(
            # self._update_graphics, -1)


    def _trigger_update_graphics(self, *largs):
        ''' Can be called multiple times and will only update once '''
        self._update_graphics_ev.cancel()
        self._update_graphics_ev()

    def _update_graphics(self, *largs):
        # Update all the graphics according to the current internal values.
        self.canvas.clear()
        add = self.canvas.add

        lh = self.line_height
        dy = lh + self.line_spacing

        # TODO del
        # adjust view if the cursor is going outside the bounds
        sx = self.scroll_x
        sy = self.scroll_y

        # draw labels
        if not self._lines or (
                not self._lines[0] and len(self._lines) == 1):
            rects = self._hint_text_rects
            labels = self._hint_text_labels
            lines = self._hint_text_lines
        else:
            rects = self._lines_rects
            labels = self._lines_labels
            lines = self._lines
        padding_left, padding_top, padding_right, padding_bottom = self.padding
        x = self.x + padding_left
        y = self.top - padding_top + sy
        miny = self.y + padding_bottom
        maxy = self.top - padding_top
        for line_num, value in enumerate(lines):
            if miny <= y <= maxy + dy:
                texture = labels[line_num]
                size = list(texture.size)
                texc = texture.tex_coords[:]

                # calcul coordinate
                viewport_pos = sx, 0
                vw = self.width - padding_left - padding_right
                vh = self.height - padding_top - padding_bottom
                tw, th = list(map(float, size))
                oh, ow = tch, tcw = texc[1:3]
                tcx, tcy = 0, 0

                # adjust size/texcoord according to viewport
                if viewport_pos:
                    tcx, tcy = viewport_pos
                    tcx = tcx / tw * (ow)
                    tcy = tcy / th * oh
                if tw - viewport_pos[0] < vw:
                    tcw = tcw - tcx
                    size[0] = tcw * size[0]
                elif vw < tw:
                    tcw = (vw / tw) * tcw
                    size[0] = vw
                if vh < th:
                    tch = (vh / th) * tch
                    size[1] = vh

                # cropping
                mlh = lh
                if y > maxy:
                    vh = (maxy - y + lh)
                    tch = (vh / float(lh)) * oh
                    tcy = oh - tch
                    size[1] = vh
                if y - lh < miny:
                    diff = miny - (y - lh)
                    y += diff
                    vh = lh - diff
                    tch = (vh / float(lh)) * oh
                    size[1] = vh

                texc = (
                    tcx,
                    tcy + tch,
                    tcx + tcw,
                    tcy + tch,
                    tcx + tcw,
                    tcy,
                    tcx,
                    tcy)

                # add rectangle.
                r = rects[line_num]
                r.pos = int(x), int(y - mlh)
                r.size = size
                r.texture = texture
                r.tex_coords = texc
                add(r)

            y -= dy

        self._update_graphics_selection()


    def update_all(self):
        _lines_labels = []
        _line_rects = []
        _create_label = self._create_line_label

        for x in self._lines:
            lbl = _create_label(x)
            _lines_labels.append(lbl)
            _line_rects.append(Rectangle(size=lbl.size))


            self._lines_labels = _lines_labels
            self._lines_rects = _line_rects



if __name__ == '__main__':
    # from kivy.app import App
    from example import ExampleApp
    app = ExampleApp()
    app.run()


'''
insert_text
    set_line_text
        _create_line_label
    refresh_text_from_property
        refresh_text
                _create_line_label
            insert_lines : << triggers update >>

            trigger_update_graphics
                update_graphics
                    canvas_clear
                    add_rects
'''
