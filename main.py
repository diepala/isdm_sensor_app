import kivy.app
import kivy.uix.boxlayout
import kivy.uix.label
import kivy.uix.button
import kivy.properties
from jnius import autoclass
import threading


class ISDMApp(kivy.app.App):

    def build(self):
        self.title_label = kivy.uix.label.Label(text='ISDM App!')
        self.bt_connect_button = kivy.uix.button.Button(text='Connect', on_release=self.connect_to_device)
        self.test_label = kivy.uix.label.Label(text='Nothing')

        self.box_layout = kivy.uix.boxlayout.BoxLayout(orientation='vertical')
        self.box_layout.add_widget(self.title_label)
        self.box_layout.add_widget(self.bt_connect_button)
        self.box_layout.add_widget(self.test_label)
        return self.box_layout

    def get_socket_stream(self, name):
        self.BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        self.BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
        self.BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
        self.UUID = autoclass('java.util.UUID')

        paired_devices = self.BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        socket = None
        for device in paired_devices:
            if device.getName() == name:
                socket = device.createRfcommSocketToServiceRecord(
                    self.UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                recv_stream = socket.getInputStream()
                send_stream = socket.getOutputStream()
                break
        socket.connect()
        return recv_stream, send_stream

    def connect_to_device(self, event):
        try:
            self.recv_stream, self.send_stream = self.get_socket_stream('HC-06')
            self.bt_connect_button.text = 'Connected!'
            self.bt_connect_button.background_normal = ''
            self.bt_connect_button.background_color = (0, 1, 0.5, 0.5)

            threading.Thread(target=self.get_data_loop).start()

        except:
            self.test_label.text = 'Disconected'

    def get_data_loop(self):
        InputStreamReader = autoclass('java.io.InputStreamReader')
        BufferedReader = autoclass('java.io.BufferedReader')
        reader = BufferedReader(InputStreamReader(self.recv_stream))
        while(True):
            data_string = reader.readLine()
            self.test_label.text = str(data_string)

if __name__=='__main__':
    isdm_app = ISDMApp()
    isdm_app.run()