from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.config import Config

from kyanvim import KyanVimEditor

from kivy.core.window import Window
Window.clearcolor = (1, 1, 1, 1)

Config.set('kivy', 'exit_on_escape', '0')
# Config.set('kivy', 'desktop', '1')
# Config.set('kivy', 'keyboard', 'system')

class RootWidget(FloatLayout):
    pass

class MyEditor(KyanVimEditor):
    pass

class DebugPanel(Widget):
    fps = StringProperty(None)

    def __init__(self, **kwargs):
        super(DebugPanel, self).__init__(**kwargs)
        Clock.schedule_once(self.update_fps)

    def update_fps(self,dt):
        self.fps = str(int(Clock.get_fps()))
        Clock.schedule_once(self.update_fps, .05)

class ExampleApp(App):
    pass

    def build(self):
        root = RootWidget()
        self.kv = root.kv_1
        root.kv_1.nvim_connect(headless=True)
        return root

    def run(self):
        super().run()


if __name__ == '__main__':
    import sys
    import cProfile, pstats, io
    pr = cProfile.Profile()
    try:
        address = sys.argv[1]
    except IndexError:
        # Neovim will just embed an instance
        address = None

    app = ExampleApp()
    # app.kv.nvim_connect()
    import logging
    def start(arg):
        logging.info('starintg profil')
        pr.enable()

    Clock.schedule_once(start, 3)
    app.run()
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    # sortby = 'tot'
    # sortby = 'calls'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())


