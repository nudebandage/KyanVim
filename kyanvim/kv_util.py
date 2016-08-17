from kivy.graphics import Canvas as BaseCanvas
from kivy.graphics import Color, Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.uix.widget import Widget as BaseWidget
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout


class CellCache():
    ''' Updating cells is cheaper than recreating them'''
    def __init__(self):
        self.cache = {}

    def set(self, row, col, rect):
        self.cache[(row, col)] = rect

    def reset(self):
        self.cache = {}


class Cell():
    def __init__(self, color, rect):
        self.color = Color
        self.rect = rect


class _Canvas(BaseCanvas):
    def create_cell(self, row, col, width, height):
        with self:
            colour = Color()
            rect = Rectangle(pos=(row*width, col*height),
                             size=(width, height))
        return Cell(colour, rect)

    def update_cell_text(self, cell, data, font_size, fg, bg):
        label = CoreLabel(text=data, font_size=font_size)
        label.refresh()
        text = label.texture
        cell.color = (bg, 1, 1)
        # cell.rect.size = text.size
        cell.rect.texture = text


class _Widget(BaseWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas = _Canvas()


class KvCanvas(FocusBehavior, _Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cell_cache = CellCache()

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        print('fdsaf')

    # TODO, CURRENTLY ONLY WORKS IF WE DESTROY ALL
    def _destroy_cells(self, top, left, bot, right):
        self._cell_cache.reset()
        self.canvas.reset()

    def _create_cells(self, top, left, bot, right, width, height):
        '''add cells'''
        for row in range(top-1, bot):
            for col in range(left, right):
                cell = self.canvas.create_cell(row, col, width, height)
                self._cell_cache.set(row, col, cell)

    def _update_cell(self, row, col, data, font_size, fg, bg):
        cell = self._cell_cache.get(row, col)
        self.canvas.update_cell_text(cell, data, font_size, fg, bg)


if __name__ == '__main__':
    from kivy.app import App
    class ExampleAppKvCanvas(KvCanvas): pass

    class blahblah(App):
        def build(self):
            return ExampleAppKvCanvas()
    app = blahblah()
    app.run()


