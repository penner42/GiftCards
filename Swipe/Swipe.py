from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import tkinter as tk


class Swipe(BoxLayout):
    def focus_inputfield(self, dt):
        self.ids.inputfield.focus = True

    def selected(self):
        Clock.schedule_once(self.focus_inputfield, -1)

    def inputfield_entered(self):
        # card not swiped
        if "%B" not in self.ids.inputfield.text:
            Clock.schedule_once(self.focus_inputfield, -1)
        else:
            pin, data = self.ids.inputfield.text.split("%B")
            self.card_swiped(pin, data)

    def card_swiped(self, pin, data):
        if data.count('?') != 2:
            self.ids.inputfield.text = pin
            Clock.schedule_once(self.focus_inputfield, -1)
        else:
            card_no = self.detect(data)
            self.ids.csv_output.text += card_no + "," + pin + "\r\n"
            self.ids.inputfield.text = ""
            Clock.schedule_once(self.focus_inputfield, -1)

    def clear_release(self, value):
        if value == "normal":
            self.ids.csv_output.text = ""
            Clock.schedule_once(self.focus_inputfield, -1)

    def copy_output(self, value):
        if value == "normal":
            #use tkinter here because Kivy clip board is broken
            tkwin = tk.Tk()
            tkwin.withdraw()
            tkwin.clipboard_append(self.ids.csv_output.text)

    def detect(self, data):
        sec1, sec2, sec3 = data.split('^')
        [t1,t2,t3] = [x.strip() for x in data.split('?')]

        # if (t1[-4:] == t2[-4:]) and (t1[-4:] != "0000"):
        if len(sec1) != 19:
            cardno = sec1[0]+sec3[14:16]+sec1[6:15]+sec3[16:20]
        else:
            cardno = sec1[0:20]

        return ' '.join(cardno[i:i+4] for i in range(0,len(cardno), 4))
    #
    # def dismiss_popup(self):
    #     self._popup.dismiss()
    #
    # def show_save(self):
    #     content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
    #     self._popup = Popup(title="Save file", content=content,
    #                         size_hint=(0.9, 0.9))
    #     self._popup.open()
    #
    # def save(self, path, filename):
    #     with open(os.path.join(path, filename), 'w') as stream:
    #         stream.write(self.ids.csv_output.text)
    #
    #     self.dismiss_popup()
    #
