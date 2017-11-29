from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

class InputWindow(BoxLayout):

    def focus_swipefield(self, dt):
        self.ids.swipefield.focus = True

    def focus_pinfield(self, dt):
        self.ids.pinfield.focus = True

    def pin_entered(self):
        Clock.schedule_once(self.focus_swipefield, -1)

    def card_swiped(self):
        if self.ids.swipefield.text.count('?') != 2:
            self.ids.swipefield.text = ""
            self.ids.swipefield.hint_text = "Swipe again"
            Clock.schedule_once(self.focus_swipefield, -1)
            return

        card_no = self.detect(self.ids.swipefield.text)
        self.ids.csv_output.text += card_no + "," + self.ids.pinfield.text.strip() + "\r\n"
        self.ids.pinfield.text = ""
        self.ids.swipefield.text = ""
        self.ids.swipefield.hint_text = "Swipe card here"
        Clock.schedule_once(self.focus_pinfield, -1)

    def clear_release(self, value):
        if value == "normal":
            self.ids.csv_output.text = ""
            Clock.schedule_once(self.focus_pinfield, -1)

    def copy_output(self, value):
        if value == "normal":
            Clipboard.copy(self.ids.csv_output.text)

    def detect(self, data):
        sec1, sec2, sec3 = data.split('^')
        [t1,t2,t3] = [x.strip() for x in data.split('?')]

        if (t1[-4:] == t2[-4:]) and (t1[-4:] != "0000"):
            cardno = sec1[2]+sec3[14:16]+sec1[8:17]+sec3[16:20]
        else:
            cardno = sec1[2:22]

        return ' '.join(cardno[i:i+4] for i in range(0,len(cardno), 4))

class SwiperApp(App):
    def build(self):
        return InputWindow()

SwiperApp().run()
