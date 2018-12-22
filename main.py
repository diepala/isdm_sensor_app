import kivy.app
import kivy.uix.boxlayout
import kivy.uix.gridlayout
import kivy.uix.label
import kivy.uix.button
from jnius import autoclass
import threading
from RyT import *
from time import time
import urllib, json

class ISDMApp(kivy.app.App):

    def build(self):
        # Presion a nivel del mar en hPa
        self.presion_mar = 1023.00
        # Intenta obtener la presion de internet
        url = "http://api.openweathermap.org/data/2.5/weather?q=barcelona&appid=c66ec6dbfe41049ac33db9af8b980f7f"
        try:
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            self.presion_mar = float(data['main']['pressure'])
        except:
            pass


        self.box_layout = kivy.uix.boxlayout.BoxLayout(orientation='vertical')
        self.title_label = kivy.uix.label.Label(text='ISDM App!')
        self.bt_connect_button = kivy.uix.button.Button(text='Connect', on_release=self.connect_to_device)
        self.test_label = kivy.uix.label.Label(text='Nothing')

       
        self.box_layout.add_widget(self.title_label)
        self.box_layout.add_widget(self.bt_connect_button)
        self.box_layout.add_widget(self.test_label)

        # T S1
        self.box_layout.add_widget(kivy.uix.label.Label(text='Temperatura S1'))
        self.t1_label = kivy.uix.label.Label()
        self.box_layout.add_widget(self.t1_label)
        # T S2
        self.box_layout.add_widget(kivy.uix.label.Label(text='Temperatura S2'))
        self.t2_label = kivy.uix.label.Label()
        self.box_layout.add_widget(self.t2_label)
        # Factor disipacion S1
        self.box_layout.add_widget(kivy.uix.label.Label(text='Factor disipación S1'))
        self.fd_label = kivy.uix.label.Label()
        self.box_layout.add_widget(self.fd_label)
        # HR
        self.box_layout.add_widget(kivy.uix.label.Label(text='HR'))
        self.HR_label = kivy.uix.label.Label()
        self.box_layout.add_widget(self.HR_label)
        # Temp HR
        self.box_layout.add_widget(kivy.uix.label.Label(text='Temperatura sensor HR'))
        self.temp_HR_label = kivy.uix.label.Label()
        self.box_layout.add_widget(self.temp_HR_label)
        # Temperatura sensor Pression
        self.box_layout.add_widget(kivy.uix.label.Label(text='Temperatura sensor Pression'))
        self.temp_P_label = kivy.uix.label.Label()
        self.box_layout.add_widget(self.temp_P_label)
        # Pression
        self.box_layout.add_widget(kivy.uix.label.Label(text='Pression atmosferica'))
        self.P_label = kivy.uix.label.Label()
        self.box_layout.add_widget(self.P_label)
        # Altura
        self.box_layout.add_widget(kivy.uix.label.Label(text='Altura'))
        self.altura_label = kivy.uix.label.Label()
        self.box_layout.add_widget(self.altura_label)      
        # Velocidad
        self.box_layout.add_widget(kivy.uix.label.Label(text='Velocidad aire'))
        self.vel_label = kivy.uix.label.Label()
        self.box_layout.add_widget(self.vel_label)

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
        data_file = open('/storage/emulated/0/datos_sensores'+str(int(time()))+'.csv', 'w')
        data_file.write('Temperatura S1 (ºC), Temperatura S2 (ºC), Factor disipacion (mW/K), Humedad (%%HR), Temperatura sensor HR (ºC), Temperatura sensor pression (ºC), Pression (hPa), Altura (m), Velocidad viento (m/s)\n')

        InputStreamReader = autoclass('java.io.InputStreamReader')
        BufferedReader = autoclass('java.io.BufferedReader')
        reader = BufferedReader(InputStreamReader(self.recv_stream))

        v0 = 0
        v1 = 0

        while(True):
            data_string = reader.readLine()
            self.test_label.text = str(data_string)
            data = [ int(d) for d in str(data_string).split('/')]

            # Temperaturas
            t1 = T_S1(140.0/(1024.0/data[0] - 1)) - 273.15
            t2 = T_S2(2200.0/(1024.0/data[1] - 1)) - 273.15
            self.t1_label.text = '%.1f ºC'%(t1)
            self.t2_label.text = '%.1f ºC'%(t2)

            # Factor disipacion
            a = data[0]/1024.0
            d = 1000.0*5.0**2*a*(1-a)/(140.0*(t1 - t2))
            self.fd_label.text = '%.1f mW/K'%(d)

            # HR y temperatura de HR
            hr_medida = 36.0 - 19.0 - (data[2] - 4130)/3.0
            self.HR_label.text = '%.1f %% HR' % (hr_medida)
            t_hr = T_SHR(10000.0/(1024.0/data[3] - 1)) - 273.15
            self.temp_HR_label.text = '%.1f ºC' % (t_hr)

            # Temperatura, pression y altura
            self.temp_P_label.text = '%.1f ºC' % (data[4]/100.0)
            self.P_label.text = '%.1f hPa' % (data[5]/100.0)
            hP = 44330.0 * (1 - (data[5]/100.0/self.presion_mar)**(1.0/5.255))
            self.altura_label.text = '%.1f m' % (hP)


            # Velocidad viento
            d0 = 1.3
            du = 0.488
            vel = ((max(d - d0, 0))/du)**1.7
            vel = (v0 + v1 + vel)/3.0
            v0 = v1
            v1 = vel
            self.vel_label.text = '%.1f m/s' % (vel)

            # Escribir a fichero
            data_file.write('%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f\n' % (t1, t2, d, hr_medida, t_hr, data[4]/100.0, data[5]/100.0, hP, vel))

if __name__=='__main__':
    isdm_app = ISDMApp()
    isdm_app.run()