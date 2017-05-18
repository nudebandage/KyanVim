
import pytest

from screen import Screen, Cell

ROWS = 10
COLS = 10

class TestScreen():
    def setup_method(self, func):
        self.screen = Screen(ROWS, COLS)

    def scroll(self, n):
        '''scroll n lines'''
        self.screen.scroll(n)

    def insert(self, row, col, data, cv_data):
        '''insert text'''
        self.screen.cursor_goto(row, col)
        self.screen.put(data)
        self.screen.get_cell(row, col).set_canvas_data(cv_data)

    def fill_screen(self, n):
        '''fill the screen with n lines'''
        for r in range(self.screen.top, self.screen.bot + 1):
            for c in range(self.screen.right + 1):
                self.insert(r, c, r, cv_data=r*2)

    def fill_should(self, row, line, text, canvas_data):
        assert len(row) == self.screen.right + 1
        for cell, t, cv_data in zip(row, text, canvas_data):
            cell.text = t
            cell.set_canvas_data(cv_data)

    def create_should(self):
        return [[Cell() for c in range(COLS)] for r in range(ROWS)]


    def test_scroll(self):
        self.fill_line(ROWS*2)
        should = self.create_should()
        for line in range(ROWS*2):
            text = str(line)*self.screen.right + 1
            cv_data = str(line*2)*self.screen.right + 1
            self.fill_should(should[line], text, cv_data)
        self.cmp(should)


    def cmp(self, should):
        for r in range(self.screen.top, self.screen.bot + 1):
            for c in range(self.screen.right + 1):
                cell = self.screen.get_cell(r, c)
                should_cell = should[r][c]
                assert cell.text == should_cell.text
                assert cell.get_canvas_data() == should_cell.get_canvas_data()


