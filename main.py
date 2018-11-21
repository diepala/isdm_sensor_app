import kivy.app
import kivy.uix.boxlayout
import kivy.uix.label

class ISDMApp(kivy.app.App):
    def build(self):
        self.title_label = kivy.uix.label.Label(text='ISDM App!')
        self.box_layout = kivy.uix.boxlayout.BoxLayout(orientation='vertical')
        self.box_layout.add_widget(self.title_label)
        return self.box_layout
    
if __name__=='__main__':
    isdm_app = ISDMApp()
    isdm_app.run()