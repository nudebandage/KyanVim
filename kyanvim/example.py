from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock

from kyanvim import KyanVimEditor

class RootWidget(BoxLayout):
    pass

class MyEditor(KyanVimEditor):
    pass

class ExampleApp(App):

    # def start(self):
        # import pdb;pdb.set_trace()
        # Starts the Kivy and the 

    def build(self):
        root = RootWidget()
        # root.kv_1.nvim_connect()
        Clock.schedule_once(lambda x:root.kv_1.nvim_connect(), 2)
        return root
        # self.root = Builder.load_file('example.kv')
        # return self.root


if __name__ == '__main__':
    import sys
    try:
        address = sys.argv[1]
    except IndexError:
        # Neovim will just embed an instance
        address = None

    app = ExampleApp()
    # while 1:
        # time.sleep(0.1)
        # pass
    app.run()


