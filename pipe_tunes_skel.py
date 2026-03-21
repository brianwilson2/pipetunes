from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

class PipeTunesApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Search input
        self.search_input = TextInput(hint_text="Search tune name...",
                                      size_hint_y=None, height=50, font_size=22)
        root.add_widget(self.search_input)

        # Scrollable area
        self.scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        root.add_widget(self.scroll)

        # Add a couple of test rows
        for i in range(5):
            lbl = Label(text=f"Test Tune {i+1}", size_hint_y=None, height=50, font_size=22)
            self.grid.add_widget(lbl)

        return root

if __name__ == "__main__":
    PipeTunesApp().run()
