from random import random as rnd
from random import choice

from kivy.graphics.texture import Texture
from kivy.cache import Cache
from kivy.graphics import Canvas as BaseCanvas
from kivy.graphics import Color, Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.uix.widget import Widget as BaseWidget
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex

from kyanvim.screen import Screen

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
        # if p:
            # print(orig, self.pos[1])
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


class _Widget(BaseWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas = _Canvas()


#TODO RENAME - > KivyNvim
class KvCanvas(FocusBehavior, _Widget):
    def __init__(self, columns, rows, *_, **kwargs):
        super().__init__(**kwargs)
        self._screen = Screen(columns, rows)

    def _destroy_cells(self, columns, rows):
        '''destory all cells and reinit the screen to columns and rows'''
        self._screen.resize(columns, rows)
        self.canvas.clear()

    def _destroy_cell_range(self, top, left, bot, right):
        kv_cells = map(lambda cell: cell.get_canvas_data(),
                       self._screen.iter_del(top, left, bot, right))
        a  = choice((1, 0, .5, .75))
        b  = choice((1, 0., .5))
        c  = choice((1, 0, .5))
        # print('deltingin', top, bot)
        for cell in kv_cells:
            # print(cell)
            # cell.canvas.clear()
            cell.k_bg_col.rgba = (a, b, c, 1)
            cell.k_fg_col.rgba = (a, b, c, 1)

    def _create_cells(self, top, left, bot, right, width, height):
        '''add cells, kivy 0,0 is bottom left'''
        # print('CREATE CELLS', top, left, bot, right)
        attrs = self._screen.attrs.ui_cache.get(None)[0]
        bg = attrs['background']
        fg = attrs['foreground']

        self._screen.resize(right + 1, bot + 1)

        for row in range(top, bot + 1):
            for col in range(left, right + 1):
                # kivy 0 is at bottom of screen, invert it with bot-row
                cell = self._screen.get_cell(row, col)
                kv_row = bot - row
                kvcell = self.canvas.create_cell(kv_row, col, width, height, bg, fg)
                cell.set_canvas_data(kvcell)
                self.add_widget(kvcell)

    def _create_cell_range(self, top, left, bot, right, width, height):
        attrs = self._screen.attrs.ui_cache.get(None)[0]
        bg = attrs['background']
        fg = attrs['foreground']

        # kivy 0 is at bottom of screen, invert it with bot-row
        abs_bot = self._screen.bot
        def gen_cells():
            for row in range(top, bot + 1):
                r = self._screen._cells[row]
                for col in range(left, right + 1):
                    cell = r[col]
                    yield row, col, cell

        # The cells are auto created in screen.scroll, we just reposition them
        for row, col, cell in gen_cells():
            kv_row = abs_bot - row
            kvcell = cell.get_canvas_data()
            pos = (col*width, kv_row*height)
            self.canvas.update_cell_pos(kvcell, pos=pos)
            kvcell = self.canvas.create_cell(kv_row, col, width, height, bg, fg)
            cell.set_canvas_data(kvcell)
            # self.add_widget(kvcell)


    def _update_cell(self, kvcell:KvCell, data:str, fg, bg):
        self.canvas.update_cell_text(kvcell, data, fg=fg, bg=bg)

    def realloc_dead_cells(self, start, stop, step, count, left, right, rowsize):
        # kivy 0 is at bottom of screen, invert it with bot-row
        # abs_bot = self._screen.bot

        # Scroll Cells that will be clipped so that they sit at the torn/new area
        clipped_cells = range(start, start + count, step)
        new_cells = range(stop, stop + count, step)
        # print('realloc', clipped_cells, new_cells)
        for clip, new in zip(clipped_cells, new_cells):
            kv_row_new = self._screen._cells[new]
            kv_row_clip = self._screen._cells[clip]
            # print('clipped widget', kv_row_clip[:5], kv_row_new[:5])
            for col in range(left, right + 1):
                kv_clip = kv_row_clip[col].get_canvas_data()
                kv_new = kv_row_new[col].get_canvas_data()
                pos_delta = kv_new.pos[1] - kv_clip.pos[1] - (step * rowsize)
                # Delete old Canvas element
                # Scroll clipped region into place
                kv_clip.scroll(pos_delta, True)
                # kv_clip.

        # for free_row, alloc_row in zip(range(f_top, f_bot), range(a_top, a_bot)):
            # print('alloc', free_row, alloc_row)
            # delta = free_row - alloc_row
            # kv_row = abs_bot - delta
            # y = delta * rowsize
            # r = self._screen._cells[free_row]
            # for col in range(left, right + 1):
                # free_cell = r[col]
                # kvcell = free_cell.get_canvas_data()
                # kvcell.scroll(y)


    def _scroll_cells(self, count, rowsize):
        print('SCROLL')
        top, bot = self._screen.top, self._screen.bot
        left, right = self._screen.left, self._screen.right

        if count > 0:
            move_top, move_bot = top + count, bot - count + 1
            start = top
            stop = bot - count + 1
            step = 1
        else:
            move_top, move_bot = top, bot + count
            start = bot
            stop = top - count - 1
            step = -1

        global a, b, c
        a  = choice((1, .5, .25, .75))
        b = 0
        c = 0

        # The following two commands only operate on the UI cells
        # Scroll the widget cells
        apply(lambda cell: cell.get_canvas_data().scroll(count*rowsize),
              self._screen.iter(move_top, left, move_bot, right))

        a = 0
        b  = choice((1, .5, .25, .75))
        c = 0

        # Realloc deletede cells to the new/torn canvas region
        self.realloc_dead_cells(start, stop, step, count, left, right, rowsize)

        # print(self._screen._cells)
        self._screen.scroll(count)
        print()
        # print(self._screen._cells)
        self.stop = 1
        return 

    def _update_cell_range(self, row, col, data:str, fg, bg):
        for i, cell in enumerate(self._screen.iter(row, col, row, col -1 + len(data))):

            self._update_cell(cell.get_canvas_data(), data[i], fg, bg)


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
            insert_lines

            trigger_update_graphics
                update_graphics
                    canvas_clear
                    add_rects
'''
