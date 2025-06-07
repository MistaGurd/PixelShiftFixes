from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp

# Diverse imports
from BGfjernelse import PixelWipe
from PDF_Merge import PDF_Merging
from Filkompromering import FilKomprimering
from Formatkonvertering import FileConvert

# Overstående er import af de klasser, som hver Python fil har.
# Hver klasse, er hver sin del (her en screen) af koden

class MainMenu(Screen):
    pass

class PixelShiftApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        Builder.load_file('GUI.kv')
        Window.maximize()
        sm = ScreenManager()
        sm.add_widget(MainMenu(name="hovedmenu"))
        sm.add_widget(PixelWipe(name="bgfjern"))
        sm.add_widget(PDF_Merging(name="pdf_merger"))
        sm.add_widget(FilKomprimering(name="filecompress"))
        sm.add_widget(FileConvert(name="formatkonvert"))
        sm.transition = NoTransition()
        return sm

if __name__ == "__main__": # Opstart af programmet
    PixelShiftApp().run()