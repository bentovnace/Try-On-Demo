from kivymd.uix.screen import MDScreen

from kivy.properties import ObjectProperty
class RootScreen(MDScreen):
    name=ObjectProperty(None) 

    textinput  = ObjectProperty(None)

    textoutput = ObjectProperty(None)
    