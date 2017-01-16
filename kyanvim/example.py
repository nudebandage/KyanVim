from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock

from kyanvim import KyanVimEditor

from kyanvim.ui_bridge import UIBridge
from kyanvim.util import attach_headless

class RootWidget(BoxLayout):
    pass

class MyEditor(KyanVimEditor):
    pass

class Test():
    pass

class ExampleApp(App):
    pass

    def build(self):
        root = RootWidget()

        # b = UIBridge()
        # test = Test()
        # nvim = attach_headless(('-u', 'NONE'), address)
        # b.connect(nvim, test)
        self.kv = root.kv_1
        root.kv_1.nvim_connect(headless=True)
        # Clock.schedule_once(lambda x, root=root:root.kv_1.nvim_connect(), 2)
        # return root
        # self.root = Builder.load_file('example.kv')
        return root

    def run(self):
        super().run()


if __name__ == '__main__':
    import sys
    try:
        address = sys.argv[1]
    except IndexError:
        # Neovim will just embed an instance
        address = None

    app = ExampleApp()
    # import pdb;pdb.set_trace()
    # app.kv.nvim_connect()
    # while 1:
        # time.sleep(0.1)
        # pass
    app.run()


