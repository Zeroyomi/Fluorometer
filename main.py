import board
import busio
import time

from kivy.app import App

from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty,\
    ListProperty
from kivy.clock import Clock

from kivy.uix.screenmanager import Screen
from kivy.core.window import Window

#hardware

import adafruit_tlc59711
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class ShowcaseScreen(Screen):
    #fullscreen = BooleanProperty(False)
   
    def add_widget(self, *args):
        if 'content' in self.ids:
            return self.ids.content.add_widget(*args)
        return super(ShowcaseScreen, self).add_widget(*args)


class ShowcaseApp(App):
    brightness = StringProperty()
    flo_read = ListProperty([0,0,0])
    hierarchy_index = ListProperty([])
    brightness ='255'
    led_on = False
    adc_gain = 1
    #adc_loop = False
    try:
        spi = busio.SPI(board.SCK, MOSI=board.MOSI)
        
    except:
        print('>>>>>>>>>>>>>>>spi init failed<<<<<<<<<<<<<<<<<<<')
    try:        
        leds = adafruit_tlc59711.TLC59711(spi, auto_show=False)
        leds[0] = (0, 0, 0)
        leds[1] = (0, 0, 0)
        leds.show()
    except:
        print('>>>>>>>>>>>>>>>led init failed<<<<<<<<<<<<<<<<<<<')
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
    except:
        print('>>>>>>>>>>>>>>>i2c init failed<<<<<<<<<<<<<<<<<<<')
    try:
        ads = ADS.ADS1115(i2c, gain=adc_gain, data_rate=8, address=0x48)
    except:
        print('>>>>>>>>>>>>>>>ads init failed<<<<<<<<<<<<<<<<<<<')        
       
    try:
        file = open("/sys/class/backlight/rpi_backlight/brightness","r")
        brightness = file.read()
        file.close()
    except:
        print('>>>>>>>>>>>>>>>Brightness init error<<<<<<<<<<<<<<<<<<<<<<<')
    
    def build(self):
        self.root = Builder.load_file('kv/main.kv')
        self.title = 'My appname'
        Window.size = (800, 480)
        
        #self.go_home()
        self.hierarchy_index.append('home')
        print(self.hierarchy_index)
        screen = Builder.load_file("./kv/home.kv")
        self.root.ids.sm.switch_to(screen, direction='right')
        self.root.ids.main_label.text = 'Choose an assay'
        self.root.ids.back_btn.disabled=True
    def go_home(self):

        if (len(self.hierarchy_index) == 1) and (self.hierarchy_index[0] == 'home'):
            return
        del self.hierarchy_index[:]
        self.hierarchy_index.append('home')
        print(self.hierarchy_index)
        screen = Builder.load_file("./kv/home.kv")
        self.root.ids.sm.switch_to(screen, direction='right')
        self.root.ids.main_label.text = 'Choose an assay'
        self.root.ids.back_btn.disabled=True

    def go_settings(self):
        if (len(self.hierarchy_index) == 1) and (self.hierarchy_index[0] == 'settings'):
            return
        del self.hierarchy_index[:]
        self.hierarchy_index.append('settings')
        print(self.hierarchy_index)
        screen = Builder.load_file("./kv/settings.kv")
        self.root.ids.sm.switch_to(screen, direction='right')
        self.root.ids.main_label.text = 'Settings'
        self.root.ids.back_btn.disabled=True

        
    def go_screen(self, screen_name):
        self.hierarchy_index.append('{0}'.format(screen_name))
        print(self.hierarchy_index)
        #self.previous_screen = self.current_screen
        #self.current_screen = screen_name
        
        screen = self.load_screen(screen_name)
        
        #sm = self.root.ids.sm
        #sm.switch_to(screen, direction='left')
        
        self.root.ids.sm.switch_to(screen, direction='left')
        self.root.ids.main_label.text = '{0}'.format(screen_name)
        self.root.ids.back_btn.disabled=False

    def go_previous(self):
        if len(self.hierarchy_index) == 2:
            if self.hierarchy_index[0] == 'home':
                self.go_home()
                return
            if self.hierarchy_index[0] == 'settings':
                self.go_settings()
                return
        
        
        self.hierarchy_index.pop()
        previous_name = self.hierarchy_index[-1]
        print(self.hierarchy_index)
        #self.previous_screen = self.current_screen
        #self.current_screen = screen_name
        
        screen = self.load_screen(previous_name)
        
        #sm = self.root.ids.sm
        #sm.switch_to(screen, direction='left')
        
        self.root.ids.sm.switch_to(screen, direction='right')
        self.root.ids.main_label.text = '{0}'.format(previous_name)
        

        
    def load_screen(self, screen_name):
        screen = Builder.load_file("./kv/{0}.kv".format(screen_name))
        return screen
        
    def blue_led_test(self):
        try:
            print("SCK, MOSI:")
            print(board.SCK)
            print(board.MOSI)
            #spi = busio.SPI(board.SCK, MOSI=board.MOSI)
            #leds = adafruit_tlc59711.TLC59711(self.spi, auto_show=False)
            if self.led_on:
                self.leds[0] = (0, 0, 0)
                self.led_on = False
                self.leds.show()
                print('Blue Led off')
                return
            else:
                self.leds[0] = (32767, 32767, 32767)
                self.led_on = True
                self.leds.show()
                print('Blue Led on')
                return
        except:
            print('Blue test false')
            
    def red_led_test(self):
        print("SCK, MOSI:")
        print(board.SCK)
        print(board.MOSI)
        #leds = adafruit_tlc59711.TLC59711(self.spi, auto_show=False)
        if self.led_on:
            self.leds[1] = (0, 0, 0)
            self.led_on = False
            self.leds.show()
            print('Red Led off')
            return
        else:
            self.leds[1] = (32767, 32767, 32767)
            self.led_on = True
            self.leds.show()
            print('Red Led on')
            return                           
        

    def adc_test(self):
        try: 
            
            #chan0 = AnalogIn(ads, ADS.P0)
            chan1 = AnalogIn(self.ads, ADS.P1)
            chan2 = AnalogIn(self.ads, ADS.P2)
            chan3 = AnalogIn(self.ads, ADS.P3)
            #print("{:>5}\t{:>5.3f}".format(chan0.value, chan0.voltage))
            while True:
                #print("channel 01 {:>5}\t{:>5.3f}".format(chan3.value, chan3.voltage))
                #print("channel 02 {:>5}\t{:>5.3f}".format(chan2.value, chan2.voltage))
                #print("channel 03 {:>5}\t{:>5.3f}".format(chan1.value, chan1.voltage))
                #print("----------------")
                adc01 = chan3.value
                adc02 = chan2.value
                adc03 = chan1.value
                print("{0}, {1}, {2}".format(adc01, adc02, adc03))
                time.sleep(0.3)
            
        except:
            print('ADC test begin false')
            
    def adc_diff(self):
        try:
            chan1 = AnalogIn(self.ads, ADS.P1)
            chan2 = AnalogIn(self.ads, ADS.P2)
            chan3 = AnalogIn(self.ads, ADS.P3)
            adc01 = chan3.value
            adc02 = chan2.value
            adc03 = chan1.value
            print("befor led {:>5}\t{:>5}\t{:>5}".format(adc01, adc02, adc03))
            
            self.leds[0] = (32767, 32767, 32767)
            self.leds.show()
            time.sleep(0.5)
            adc01_af = chan3.value
            adc02_af = chan2.value
            adc03_af = chan1.value 
            print("after led {:>5}\t{:>5}\t{:>5}".format(adc01_af, adc02_af, adc03_af))
            adc01 = adc01_af - adc01
            adc02 = adc02_af - adc02
            adc03 = adc03_af - adc03

            print("after dif {:>5}\t{:>5}\t{:>5}".format(adc01, adc02, adc03))
            print("---------------------------------------")
            self.leds[0] = (0, 0, 0)
            self.leds.show()
        
        except:
            print('ADC diff test failed')
            
    def adc_aver(self):
        try:
            chan1sum = 0
            chan2sum = 0
            chan3sum = 0
            chan1 = AnalogIn(self.ads, ADS.P1)
            chan2 = AnalogIn(self.ads, ADS.P2)
            chan3 = AnalogIn(self.ads, ADS.P3)
            for i in range(10):
                chan1read = chan1.value
                chan2read = chan2.value
                chan3read = chan3.value
                chan1sum = chan1sum + chan1read
                chan2sum = chan2sum + chan2read
                chan3sum = chan3sum + chan3read
                print(str(chan3read) +" "+str(chan2read) +" "+ str(chan1read))
            print('ADC average: ')
            print(chan3sum/10)   
            print(chan2sum/10)
            print(chan1sum/10)
            self.flo_read[0] = str(chan3sum/10)
            self.flo_read[1] = str(chan2sum/10)
            self.flo_read[2] = str(chan1sum/10)
        except:
            print('ADC average test failed')
            
    def adc_aver_with_led(self):
        try:
            self.leds[0] = (32767, 32767, 32767)
            self.leds.show()
            time.sleep(0.3)
            chan1sum = 0
            chan2sum = 0
            chan3sum = 0
            chan1 = AnalogIn(self.ads, ADS.P1)
            chan2 = AnalogIn(self.ads, ADS.P2)
            chan3 = AnalogIn(self.ads, ADS.P3)
            for i in range(10):
                chan1read = chan1.value
                chan2read = chan2.value
                chan3read = chan3.value
                chan1sum = chan1sum + chan1read
                chan2sum = chan2sum + chan2read
                chan3sum = chan3sum + chan3read
                print(str(chan3read) +" "+str(chan2read) +" "+ str(chan1read))
                time.sleep(0.3)
            print("result led always on: ")
            print(str(chan3sum/10)+" "+str(chan2sum/10)+" "+str(chan1sum/10))
            self.leds[0] = (0, 0, 0)
            self.leds.show()
            self.flo_read[0] = str(chan3sum/10)
            self.flo_read[1] = str(chan2sum/10)
            self.flo_read[2] = str(chan1sum/10)
        
        except:
            print('ADC average led always on failed')
            
    def adc_aver_with_blink(self):
        
        try:
            chan1sum = 0
            chan2sum = 0
            chan3sum = 0
            chan1 = AnalogIn(self.ads, ADS.P1)
            chan2 = AnalogIn(self.ads, ADS.P2)
            chan3 = AnalogIn(self.ads, ADS.P3)
           
            for i in range(10):
                self.leds[0] = (32767, 32767, 32767)
                self.leds.show()
                time.sleep(0.3)
                chan1read = chan1.value
                chan2read = chan2.value
                chan3read = chan3.value
                chan1sum = chan1sum + chan1read
                chan2sum = chan2sum + chan2read
                chan3sum = chan3sum + chan3read
                print(str(chan3read) +" "+str(chan2read) +" "+ str(chan1read))
                self.leds[0] = (0, 0, 0)
                self.leds.show()
                time.sleep(0.3)
            print("result blink: ")
            print(str(chan3sum/10)+" "+str(chan2sum/10)+" "+str(chan1sum/10))
            self.flo_read[0] = str(chan3sum/10)
            self.flo_read[1] = str(chan2sum/10)
            self.flo_read[2] = str(chan1sum/10)
            #self.root.ids.flo_read1.text = '{0}'.format(str(chan3sum/10))
            #self.root.ids.flo_read2.text = '{0}'.format(str(chan2sum/10))
            #self.root.ids.flo_read3.text = '{0}'.format(str(chan1sum/10))
        except:
            print('ADC average blink failed')
        
    def brightness_control(self, *args):
        self.brightness = str(int(args[1]))
        try:
            file = open("/sys/class/backlight/rpi_backlight/brightness","w")
            file.write(self.brightness)
            file.close()
        except:
            print('Brightness error')
        
        
        
if __name__ == '__main__':
    ShowcaseApp().run()