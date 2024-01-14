import os 
import importlib
from kivy.core.window import Window
from kivymd.app import MDApp
from kaki.app import App
from kivymd.uix.screen import MDScreen
from kivy import platform
import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()

if platform=='android':
    from android.permissions import Permission,request_permissions
    request_permissions([Permission.INTERNET,Permission.CAMERA,Permission.WRITE_EXTERNAL_STORAGE,Permission.READ_EXTERNAL_STORAGE,Permission.RECORD_AUDIO])
class RootScreen(MDScreen):
    pass 




Window.size = (504,753)

class VitualTryOn(App,  MDApp):
    
    KV_FILES = {
        os.path.join(os.getcwd(),
            "Screens",
            "RootScreen",
            "root_screen.kv",


        ),

        os.path.join(os.getcwd(),
            "Screens",
            "CameraScreen",
            "camera_screen.kv",


        ),
        os.path.join(os.getcwd(),
            "Screens",
            "ChooseClothesScreen",
            "choose_clothes_screen.kv",


        ),

       


       
    }

    
    CLASSES = {
        "RootScreen":"root_screen",
        "CameraScreen":"Screens.CameraScreen.camera_screen",
        "ChooseClothesScreen":"Screens.ChooseClothesScreen.choose_clothes_screen"
        
       



    }
    AUTORELOADER_PATHS = [
        (".",{"recursive":True}),

    ]

    def build_app(self):
        self.theme_cls.primary_palette ="Orange"
        import Screens.RootScreen.root_screen

       
        importlib.reload(Screens.RootScreen.root_screen)
  
        n = RootScreen()
      
       
        return Screens.RootScreen.root_screen.RootScreen()

  
    def on_leave(self):
        print('leave')
    
    def on_pause(self):
        return True

            


         
if __name__ == "__main__":
   VitualTryOn().run()
