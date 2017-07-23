"""Common code for graphical and text UIs."""
__all__ = ('Screen',)

from copy import copy

from kivy.utils import get_color_from_hex

from kyanvim.util import _stringify_color
from kyanvim.util import _split_color, _invert_color


class Cell(object):
    def __init__(self):
        self.text = ' '
        self.attrs = None
        self.canvas_data = None 
    def __repr__(self):
        return self.text

    def get(self):
        return self.text, self.attrs

    def set(self, text, attrs):
        self.text = text
        self.attrs = attrs

    def set_canvas_data(self, data):
        self.canvas_data = data

    def get_canvas_data(self):
        return self.canvas_data

class DirtyRange():
    ''' Record sections that are dirty '''
    def __init__(self, top, left, bot, right):
        self.top = top
        self.left = left
        self.bot = bot
        self.right = right

    def __repr__(self):
        return "%s.%s - %s.%s" % (self.top, self.left, self.bot, self.right)

class DirtyState():
    '''
    Return information about cells that require updating
    '''
    def __init__(self):
        self.dirty_ranges = []

    def changed(self, top, left, bot, right):
        '''mark some section as being dirty'''
        # if self.dirty_ranges:
            # last = self.dirty_ranges[-1]
            # if last.right == left and last.bot == top:
                # last.right = right
                # last.bot = bot
                # return
        self.dirty_ranges.append(DirtyRange(top, left, bot, right))

    def get(self):
        ''' get the areas that are dirty, call is_dirty first'''
        for rng in self.dirty_ranges:
            yield rng.top, rng.left, rng.bot, rng.right

    def reset(self):
        '''mark the state as being not dirty'''
        self.dirty_ranges = []

    def is_dirty(self):
        if self.dirty_ranges:
            return True
        return False


class UiAttrsCache():
    def __init__(self):
        self.cache = {}

    def init(self, attrs):
        self.attrs = attrs

    def reset(self):
        self.cache = {}

    def get(self, nvim_attrs):
        '''
        nvim_attrs to ui_attrs
        uses a cache
        '''
        # TODO abstract
        # colour of -1 means we can use our own default
        # n = normal, c = cursor
        hash = tuple(sorted((k, v,) for k, v in (nvim_attrs or {}).items()))
        rv = self.cache.get(hash, None)
        if rv is None:
            fg = self.attrs.defaults.get('foreground')
            fg = fg if fg != -1 else 0
            bg = self.attrs.defaults.get('background')
            bg = bg if bg != -1 else 0xffffff

            n = {'foreground': _split_color(fg),
                'background': _split_color(bg),}

            if nvim_attrs:
                # make sure that fg and bg are assigned first
                for k in ['foreground', 'background']:
                    if k in nvim_attrs:
                        n[k] = _split_color(nvim_attrs[k])
                for k, v in nvim_attrs.items():
                    if k == 'reverse':
                        n['foreground'], n['background'] = \
                            n['background'], n['foreground']
                    elif k == 'italic':
                        n['slant'] = 'italic'
                    elif k == 'bold':
                        n['weight'] = 'bold'
                        # TODO
                        # if self._bold_spacing:
                            # n['letter_spacing'] \
                                    # = str(self._bold_spacing)
                    elif k == 'underline':
                        n['underline'] = '1'
            c = dict(n)
            c['foreground'] = _invert_color(*_split_color(fg))
            c['background'] = _invert_color(*_split_color(bg))
            c['foreground'] = _stringify_color(*c['foreground'])
            c['background'] = _stringify_color(*c['background'])
            n['foreground'] = get_color_from_hex(_stringify_color(*n['foreground']))
            n['background'] = get_color_from_hex(_stringify_color(*n['background']))
            rv = (n, c)
            self.cache[hash] = rv
        return rv


class Attrs():
    '''
    Helper to abstract efficiently handling the attributes
    '''
    def __init__(self):
        # Default attrs to be applie unless next is set to overide
        self.defaults = {}
        self.ui_cache = UiAttrsCache()
        self.ui_cache.init(self)

    def set_default(self, k, v):
        self.defaults[k] = v
        # The cache holds values computed using the defaults so reset!
        self.ui_cache.reset()

    def set_next(self, nvim_attrs):
        '''
        the next put will have these settings,
	Set the attributes that the next text put on the screen will have.
	`attrs` is a dict. Any absent key is reset to its default value.
        the attrs are changed to conform to the ui spec
        '''
        self.next = self.ui_cache.get(nvim_attrs)

    def get_next(self):
        return self.next

class Screen(object):

    """Store nvim screen state."""

    def __init__(self, columns, rows):
        """Initialize the Screen instance."""
        self.columns = columns
        self.rows = rows
        self.row = 0
        self.col = 0
        self.top = 0
        self.bot = rows - 1
        self.left = 0
        self.right = columns - 1
        self._cells = [[Cell() for c in range(columns)] for r in range(rows)]
        self.attrs = Attrs()
        self._dirty = DirtyState()
        self._dirty.changed(self.top, self.left, self.bot, self.right)

    def resize(self, cols , rows):
        # attrs shoild stick around
        attrs = self.attrs
        self.__init__(cols, rows)
        self.attrs = attrs

    def clear(self):
        """Clear the screen."""
        self._clear_region(self.top, self.left, self.bot, self.right)

    def eol_clear(self):
        """Clear from the cursor position to the end of the scroll region."""
        self._clear_region(self.row, self.col, self.row, self.right)

    def cursor_goto(self, row, col):
        """Change the virtual cursor position."""
        self.row = row
        self.col = col

    def set_scroll_region(self, top, bot, left, right):
        """Change scroll region."""
        self.top = top
        self.bot = bot
        self.left = left
        self.right = right

    def scroll(self, count):
        """Shift scroll region."""
        top, bot = self.top, self.bot
        left, right = self.left, self.right
        if count > 0:
            start = top
            stop = bot - count + 1
            step = 1
        else:
            start = bot
            stop = top - count - 1
            step = -1

        # Hold clipped cells that will be deleted by the shift
        clipped_cells = []
        for clip in range(start, start + count, step):
            new_row = []
            source_row = self._cells[clip]
            for col in range(left, right + 1):
                new_row.append(source_row[col].get_canvas_data())
            clipped_cells.append(new_row)

        # shift the cells, clipped cells now overwritten
        for row in range(start, stop, step):
            target_row = self._cells[row]
            source_row = self._cells[row + count]
            for col in range(left, right + 1):
                target_row[col] = copy(source_row[col])

        # clear invalid cells
        for row in range(stop, stop + count, step):
            self._clear_region(row, row, left, right)


    def put(self, text):
        """Put character on virtual cursor position."""
        cell = self._cells[self.row][self.col]
        # TODO put a None if the attrs is the same as the last char...  would also need to update iter so that it retuns the last
        # result if the attrs == None
        cell.set(text, self.attrs.get_next())
        self._dirty.changed(self.row, self.col, self.row, self.col)
        self.cursor_goto(self.row, self.col + 1)

    def get_cell(self, row, col):
        """Get cell at row, col."""
        return self._cells[row][col]

    def get_cursor(self):
        """Get text, attrs at the virtual cursor position."""
        return self.get_cell(self.row, self.col).get()

    def iter(self, top, left, bot, right):
        """iter over cells"""
        for row in range(top, bot + 1):
            r = self._cells[row]
            for col in range(left, right + 1):
                cell = r[col]
                yield cell

    def iter_pos(self, top, left, bot, right):
        for row in range(top, bot + 1):
            r = self._cells[row]
            for col in range(left, right + 1):
                cell = r[col]
                yield row, col, cell


    def iter_del(self, top, left, bot, right):
        for cell in self.iter(top, left, bot, right):
            yield cell

        # Full line
        if len(self._cells[0]) == right + 1 - left:
            print('DEL FULL LINE', self._cells[top:bot])
            del self._cells[top:bot+1]
        # partial
        else:
            for row in self._cells:
                del row[left:right+1]

    def iter_text(self, startrow, endrow, startcol, endcol):
        """Extract text/attrs at row, startcol-endcol."""
        for row in range(startrow, endrow + 1):
            r = self._cells[row]
            cell = r[startcol]
            curcol = startcol
            attrs = cell.attrs
            buf = [cell.text]
            for col in range(startcol + 1, endcol + 1):
                cell = r[col]
                if cell.attrs != attrs or not cell.text:
                    yield row, curcol, ''.join(buf), attrs
                    attrs = cell.attrs
                    buf = [cell.text]
                    curcol = col
                    if not cell.text:
                        # glyph uses two cells, yield a separate entry
                        yield row, curcol, '', self.attrs.ui_cache.get(None)
                        curcol += 1
                else:
                    buf.append(cell.text)
            if buf:
                yield row, curcol, ''.join(buf), attrs

    def _clear_region(self, top, left, bot, right):
        for rownum in range(top, bot + 1):
            row = self._cells[rownum]
            for colnum in range(left, right + 1):
                cell = row[colnum]
                cell.set(' ', self.attrs.ui_cache.get(None))
        self._dirty.changed(top, left, bot, right)

    def iter_create(self, top, left, bot, right):
        '''
        create cells and yields them
        '''

        columns = right + 1 -left
        rows = top - bot + 1

        attrs = self.attrs.ui_cache.get(None)
        new_cells = [[Cell() for c in range(columns)] for r in range(rows)]
        map(lambda x: x.set_cell(' ', attrs), new_cells)

        # Full line
        import pdb;pdb.set_trace()
        if len(self._cells[0]) == columns:
            for i, row in enumerate(new_cells):
                self._cells.insert(top + i, row)
        # partial
        else:
            for i, row in enumerate(new_cells):
                for j, col in enumerate(row):
                    self._cells[top + i].insert(left +j, col)

        import pdb;pdb.set_trace()
        for row in range(top, bot + 1):
            r = self._cells[row]
            for col in range(left, right + 1):
                cell = r[col]
                yield row, col, cell
