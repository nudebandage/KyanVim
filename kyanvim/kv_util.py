from kivy.graphics import Canvas as BaseCanvas
from kivy.graphics import Color, Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.uix.widget import Widget as BaseWidget
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from random import random as r

class CellCache():
    ''' Updating cells is cheaper than recreating them'''
    def __init__(self):
        self.cache = {}

    def set(self, row, col, rect):
        self.cache[(row, col)] = rect

    def get(self, row, col):
        return self.cache.get((row, col))

    def reset(self):
        self.cache = {}


class Cell():
    def __init__(self, color, rect):
        self.color = Color
        self.rect = rect


# label = Label(text='0')

class _Canvas(BaseCanvas):
    def create_cell(self, row, col, width, height):
        # label.text = str(int(label.text) + 1)
        with self:
            colour = Color(r(), 1, 1, mode='hsv')
            rect = Rectangle(pos=(col*width, row*height),
                             size=(width, height))
        return Cell(colour, rect)

    def update_cell_text(self, cell, data, font_size, fg, bg):
        label = CoreLabel(text=data, font_size=font_size)
        label.refresh()
        text = label.texture
        # cell.color = (bg, 1, 1)
        cell.rect.size = text.size
        cell.rect.texture = text


class _Widget(BaseWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas = _Canvas()
        # self.add_widget(label)


class KvCanvas(FocusBehavior, _Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cell_cache = CellCache()

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        print('fdsaf')

    # TODO, CURRENTLY ONLY WORKS IF WE DESTROY ALL
    def _destroy_cells(self, top, left, bot, right):
        # print('DESTROY CELLS')
        self._cell_cache.reset()
        self.canvas.clear()

    def _create_cells(self, top, left, bot, right, width, height):
        '''add cells, kivy 0,0 is bottom left'''
        print('CREATE CELLS', top, left, bot, right)
        for _row in range(top, bot + 1):
            for col in range(left, right + 1):
                # kivy 0 is at bottom of screen, invert it with bot-row

                # row = _row
                # print(row)
                row = bot - _row
                cell = self.canvas.create_cell(row, col, width, height)
                self._cell_cache.set(row, col, cell)

    def _update_cell(self, _row, col, data, font_size, fg, bg, bot):
        # print('UPDATE CELLS', row, col, data)
        row = bot - _row
        cell = self._cell_cache.get(row, col)
        self.canvas.update_cell_text(cell, data, font_size, fg, bg)


if __name__ == '__main__':
    # from kivy.app import App
    from example import ExampleApp
    app = ExampleApp()
    app.run()


