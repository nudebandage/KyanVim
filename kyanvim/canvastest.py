from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
# from kivy.core.text import CoreLabel
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color
from kivy.graphics import Rectangle

class HVObject(BoxLayout):
    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)
        self.colour = 1
        self.label = Label()
        self.render()
        self.add_widget(self.label)

        self.bind(size=self._update_rect, pos=self._update_rect)
        Clock.schedule_interval(self.callevery, 1)

    def render(self):
        self.canvas.clear()
        self.canvas.add(Color(1-self.colour, self.colour, 0, 1))
        self.rect = Rectangle(size=self.size, pos=self.pos)
        self.canvas.add(self.rect)
        label = CoreLabel(text="COL %d" % self.colour, font_size=20)
        label.refresh()
        text = label.texture
        self.canvas.add(Color(self.colour, 1-self.colour,0, 1))
        pos = list(self.pos[i] + (self.size[i] - text.size[i]) / 2 for i in range(2))
        self.canvas.add(Rectangle(size=text.size, pos=pos, texture=text))
        self.canvas.ask_update()

    def callevery(self, x):
        self.colour = 1-self.colour
        self.render()

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        self.label.pos = instance.pos


class ExampleApp(App):
    def build(self):
        return HVObject()

app = ExampleApp()
app.run()
