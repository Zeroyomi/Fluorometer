import board
import busio

import time,threading
import configparser


from kivy.app import App

from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty,\
    ListProperty, ObjectProperty
from kivy.clock import Clock

from kivy.uix.screenmanager import Screen
from kivy.core.window import Window

#for popup
from kivy.factory import Factory
from kivy.uix.popup import Popup

#for table
from kivy_garden.graph import Graph, MeshLinePlot, SmoothLinePlot, MeshStemPlot, PointPlot, ScatterPlot

#hardware
import adafruit_tlc59711
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class PopupBox(Popup):
    pop_up_text = ObjectProperty()
    def update_pop_up_text(self, p_message):
        self.pop_up_text.text = p_message
    def set_bar(self, value):
        self.reading_progress_bar.value = value

class ShowcaseScreen(Screen):
    #fullscreen = BooleanProperty(False)
   
    def add_widget(self, *args):
        if 'content' in self.ids:
            return self.ids.content.add_widget(*args)
        return super(ShowcaseScreen, self).add_widget(*args)


class ShowcaseApp(App):
    #kivy properties
    brightness = StringProperty()
    flo_read = ListProperty([0,0,0])
    hierarchy_index = ListProperty([])
    DNA_result = StringProperty()
    adc_gain = StringProperty()
    sample_rate = StringProperty()
    #config
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    #brightness =config['BASIC']['brightness']
    led_red_on = False
    led_blue_on = False
    adc_gain = '1'
    sample_rate = '8'
    unit = NumericProperty(1)
    home_screen = Builder.load_file("./kv/home.kv")
    setting_screen = Builder.load_file("./kv/settings.kv")
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
    #try:
        #ads = ADS.ADS1115(i2c, gain=adc_gain, data_rate=sample_rate, address=0x48)
    #except:
        #print('>>>>>>>>>>>>>>>ads init failed<<<<<<<<<<<<<<<<<<<')        
       
    try:
        file = open("/sys/class/backlight/rpi_backlight/brightness","r")
        brightness = file.read()
        file.close()
    except:
        print('>>>>>>>>>>>>>>>Brightness init error<<<<<<<<<<<<<<<<<<<<<<<')
    
    def build(self):
        self.root = Builder.load_file('kv/main.kv')
        self.title = 'Fluorometer'
        Window.size = (800, 480)
        
        #self.go_home()
        self.hierarchy_index.append('home')
        print(self.hierarchy_index)
        #screen = Builder.load_file("./kv/home.kv")
        self.root.ids.sm.switch_to(self.home_screen, direction='right')
        self.root.ids.main_label.text = 'Choose an assay'
        self.root.ids.back_btn.disabled=True
        
    def go_home(self):

        if (len(self.hierarchy_index) == 1) and (self.hierarchy_index[0] == 'home'):
            return
        del self.hierarchy_index[:]
        self.hierarchy_index.append('home')
        print(self.hierarchy_index)
        #screen = Builder.load_file("./kv/home.kv")
        self.root.ids.sm.switch_to(self.home_screen, direction='right')
        self.root.ids.main_label.text = 'Choose an assay'
        self.root.ids.back_btn.disabled=True

    def go_settings(self):
        if (len(self.hierarchy_index) == 1) and (self.hierarchy_index[0] == 'settings'):
            return
        del self.hierarchy_index[:]
        self.hierarchy_index.append('settings')
        print(self.hierarchy_index)
        #screen = Builder.load_file("./kv/settings.kv")
        self.root.ids.sm.switch_to(self.setting_screen, direction='right')
        self.root.ids.main_label.text = 'Settings'
        self.root.ids.back_btn.disabled=True

        
    def go_screen(self, screen_name):
        if (self.hierarchy_index[-1] != screen_name):
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
    
#-----------------------------Settings---------------------------------
    def brightness_control(self, *args):
        self.brightness = str(int(args[1]))
        try:
            file = open("/sys/class/backlight/rpi_backlight/brightness","w")
            file.write(self.brightness)
            file.close()
        except:
            print('Brightness error')
            
    def blue_led_test(self):
        try:
            print("SCK, MOSI:")
            print(board.SCK)
            print(board.MOSI)
            if self.led_blue_on:
                self.leds[1] = (0, 0, 0)
                self.led_blue_on = False
                self.leds.show()
                print('Blue Led off')
                return
            else:
                self.leds[1] = (65535, 65535, 65535)
                self.led_blue_on = True
                self.leds.show()
                print('Blue Led on')
                return
        except:
            print('Blue test false')
            
    def red_led_test(self):
        print("SCK, MOSI:")
        print(board.SCK)
        print(board.MOSI)
        if self.led_red_on:
            self.leds[0] = (0, 0, 0)
            self.led_red_on = False
            self.leds.show()
            print('Red Led off')
            return
        else:
            self.leds[0] = (65535, 65535, 65535)
            self.led_red_on = True
            self.leds.show()
            print('Red Led on')
            return                           

    def adc_test(self):
        try: 
            gain_input = float(self.adc_gain)
            sample_rate_input = float(self.sample_rate)
            ads = ADS.ADS1115(self.i2c,gain=gain_input , data_rate=sample_rate_input, address=0x48)
            #chan0 = AnalogIn(ads, ADS.P0)
            chan1 = AnalogIn(ads, ADS.P1)
            chan2 = AnalogIn(ads, ADS.P2)
            chan3 = AnalogIn(ads, ADS.P3)
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
            gain_input = float(self.adc_gain)
            sample_rate_input = float(self.sample_rate)
            ads = ADS.ADS1115(self.i2c,gain=gain_input , data_rate=sample_rate_input, address=0x48)
            chan1 = AnalogIn(ads, ADS.P1)
            chan2 = AnalogIn(ads, ADS.P2)
            chan3 = AnalogIn(ads, ADS.P3)
            adc01 = chan3.value
            adc02 = chan2.value
            adc03 = chan1.value
            print("befor led {:>5}\t{:>5}\t{:>5}".format(adc01, adc02, adc03))
            
            self.leds[0] = (65535, 65535, 65535)
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

    def time_test(self):
        ads = ADS.ADS1115(self.i2c,gain=1 , data_rate=8, address=0x48)
        chan2 = AnalogIn(ads, ADS.P2)
        self.leds[1] = (65535, 65535, 65535)
        self.leds.show()
        for i in range(20):
            print(time.ctime())
            print(chan2.value)
            print(chan2.value)
            print(chan2.value)
            print(chan2.value)
            print(chan2.value)
            time.sleep(30)
        self.leds[1] = (0,0,0)
        self.leds.show()

#-----------------------------Fluorometer---------------------------------
    def show_popup(self):
        self.pop_up = Factory.PopupBox()
        self.pop_up.update_pop_up_text('Reading...')
        self.pop_up.open()        
       
            
    def adc_aver_thread(self):
        try:
            pro_bar = 0
            gain_input = float(self.adc_gain)
            sample_rate_input = float(self.sample_rate)
            ads = ADS.ADS1115(self.i2c,gain=gain_input , data_rate=sample_rate_input, address=0x48)
            chan1sum = 0
            chan2sum = 0
            chan3sum = 0
            chan1 = AnalogIn(ads, ADS.P1)
            chan2 = AnalogIn(ads, ADS.P2)
            chan3 = AnalogIn(ads, ADS.P3)
            for i in range(10):
                chan1read = chan1.value
                chan2read = chan2.value
                chan3read = chan3.value
                chan1sum = chan1sum + chan1read
                chan2sum = chan2sum + chan2read
                chan3sum = chan3sum + chan3read
                print(str(chan3read) +" "+str(chan2read) +" "+ str(chan1read))
                pro_bar += 10
                self.pop_up.set_bar(pro_bar)
            print('ADC average: ')
            print(chan3sum/10)   
            print(chan2sum/10)
            print(chan1sum/10)
            self.flo_read[0] = str(chan3sum/10)
            self.flo_read[1] = str(chan2sum/10)
            self.flo_read[2] = str(chan1sum/10)
            self.pop_up.dismiss()
        except:
            self.pop_up.dismiss()
            print('ADC average test failed')
            
    def adc_aver_with_led_thread(self):
        try:
            pro_bar = 0
            gain_input = float(self.adc_gain)
            sample_rate_input = float(self.sample_rate)
            ads = ADS.ADS1115(self.i2c,gain=gain_input , data_rate=sample_rate_input, address=0x48)
            self.leds[1] = (65535, 65535, 65535)
            self.leds.show()
            time.sleep(0.3)
            chan1sum = 0
            chan2sum = 0
            chan3sum = 0
            chan1 = AnalogIn(ads, ADS.P1)
            chan2 = AnalogIn(ads, ADS.P2)
            chan3 = AnalogIn(ads, ADS.P3)
            for i in range(10):
                chan1read = chan1.value
                chan2read = chan2.value
                chan3read = chan3.value
                chan1sum = chan1sum + chan1read
                chan2sum = chan2sum + chan2read
                chan3sum = chan3sum + chan3read
                print(str(chan3read) +" "+str(chan2read) +" "+ str(chan1read))
                time.sleep(0.3)
                pro_bar += 10
                self.pop_up.set_bar(pro_bar)
            print("result led always on: ")
            print(str(chan3sum/10)+" "+str(chan2sum/10)+" "+str(chan1sum/10))
            self.leds[1] = (0, 0, 0)
            self.leds.show()
            self.flo_read[0] = str(chan3sum/10)
            self.flo_read[1] = str(chan2sum/10)
            self.flo_read[2] = str(chan1sum/10)
            self.pop_up.dismiss()
        except:
            self.pop_up.dismiss()
            print('ADC average led always on failed')
    
   
    def adc_aver_with_blink_thread(self):
        try:
            pro_bar = 0
            gain_input = float(self.adc_gain)
            sample_rate_input = float(self.sample_rate)
            ads = ADS.ADS1115(self.i2c,gain=gain_input , data_rate=sample_rate_input, address=0x48)
            chan1sum = 0
            chan2sum = 0
            chan3sum = 0
            chan1 = AnalogIn(ads, ADS.P1)
            chan2 = AnalogIn(ads, ADS.P2)
            chan3 = AnalogIn(ads, ADS.P3)
           
            for i in range(10):
                self.leds[1] = (65535, 65535, 65535)
                self.leds.show()
                time.sleep(0.3)
                chan1read = chan1.value
                chan2read = chan2.value
                chan3read = chan3.value
                chan1sum = chan1sum + chan1read
                chan2sum = chan2sum + chan2read
                chan3sum = chan3sum + chan3read
                print(str(chan3read) +" "+str(chan2read) +" "+ str(chan1read))
                self.leds[1] = (0, 0, 0)
                self.leds.show()
                time.sleep(0.3)
                pro_bar += 10
                self.pop_up.set_bar(pro_bar)
            print("result blink: ")
            print(str(chan3sum/10)+" "+str(chan2sum/10)+" "+str(chan1sum/10))
            self.flo_read[0] = str(chan3sum/10)
            self.flo_read[1] = str(chan2sum/10)
            self.flo_read[2] = str(chan1sum/10)
            self.pop_up.dismiss()
        except:
            self.pop_up.dismiss()
            print('ADC average blink failed')
           
    def adc_aver(self):
        self.show_popup()
        mythread = threading.Thread(target=self.adc_aver_thread)
        mythread.start()
        
    def adc_aver_with_led(self):
        self.show_popup()
        mythread = threading.Thread(target=self.adc_aver_with_led_thread)
        mythread.start()
        
    def adc_aver_with_blink(self):
        self.show_popup()
        mythread = threading.Thread(target=self.adc_aver_with_blink_thread)
        mythread.start()
#-----------------------------DNA---------------------------------        
    def read_standard_1_thread(self):
        print('read stadndard 1')
        fake_read = 0
        '''
        bar = 0
        for i in range(5):
            bar = bar + 20
            self.pop_up.set_bar(bar)
            time.sleep(0.2)
        fake_read = 22
        '''
        try:
            pro_bar = 0
            gain_input = float(self.adc_gain)
            sample_rate_input = float(self.sample_rate)
            ads = ADS.ADS1115(self.i2c,gain=gain_input , data_rate=sample_rate_input, address=0x48)
            chan1sum = 0
            chan2sum = 0
            chan3sum = 0
            chan1 = AnalogIn(ads, ADS.P1)
            chan2 = AnalogIn(ads, ADS.P2)
            chan3 = AnalogIn(ads, ADS.P3)
           
            for i in range(10):
                self.leds[1] = (65535, 65535, 65535)
                self.leds.show()
                time.sleep(0.3)
                chan1read = chan1.value
                chan2read = chan2.value
                chan3read = chan3.value
                chan1sum = chan1sum + chan1read
                chan2sum = chan2sum + chan2read
                chan3sum = chan3sum + chan3read
                #print(str(chan3read) +" "+str(chan2read) +" "+ str(chan1read))
                self.leds[1] = (0, 0, 0)
                self.leds.show()
                time.sleep(0.3)
                pro_bar += 10
                self.pop_up.set_bar(pro_bar)
            #print("result blink: ")
            #print(str(chan3sum/10)+" "+str(chan2sum/10)+" "+str(chan1sum/10))
            self.flo_read[0] = str(chan3sum/10)
            self.flo_read[1] = str(chan2sum/10)
            self.flo_read[2] = str(chan1sum/10)
            fake_read = chan1sum/10
           
        except:
            self.pop_up.dismiss()
            print('standard 1 read failed')
        print(fake_read)
        ShowcaseApp.config['DNA']['g'] = str(fake_read)
        with open('config.ini', 'w') as configfile:
            ShowcaseApp.config.write(configfile)

            
        #self.root.ids.sm.get_screen('Standard Table').ids.plot_dna.add_plot(self.plot)    
        self.pop_up.dismiss()
        
    def read_standard_2_thread(self):
        fake_read = 0
        print('read stadndard 2')
        '''
        bar = 0
        for i in range(5):
            bar = bar + 20
            self.pop_up.set_bar(bar)
            time.sleep(0.2)
        fake_read = 60
        '''
        try:
            pro_bar = 0
            gain_input = float(self.adc_gain)
            sample_rate_input = float(self.sample_rate)
            ads = ADS.ADS1115(self.i2c,gain=gain_input , data_rate=sample_rate_input, address=0x48)
            chan1sum = 0
            chan2sum = 0
            chan3sum = 0
            chan1 = AnalogIn(ads, ADS.P1)
            chan2 = AnalogIn(ads, ADS.P2)
            chan3 = AnalogIn(ads, ADS.P3)
           
            for i in range(10):
                self.leds[1] = (65535, 65535, 65535)
                self.leds.show()
                time.sleep(0.3)
                chan1read = chan1.value
                chan2read = chan2.value
                chan3read = chan3.value
                chan1sum = chan1sum + chan1read
                chan2sum = chan2sum + chan2read
                chan3sum = chan3sum + chan3read
                #print(str(chan3read) +" "+str(chan2read) +" "+ str(chan1read))
                self.leds[1] = (0, 0, 0)
                self.leds.show()
                time.sleep(0.3)
                pro_bar += 10
                self.pop_up.set_bar(pro_bar)
            #print("result blink: ")
            #print(str(chan3sum/10)+" "+str(chan2sum/10)+" "+str(chan1sum/10))
            self.flo_read[0] = str(chan3sum/10)
            self.flo_read[1] = str(chan2sum/10)
            self.flo_read[2] = str(chan1sum/10)
            fake_read = chan1sum/10
            
        except:
            self.pop_up.dismiss()
            print('standard 2 read failed')
        print(fake_read)   
        ShowcaseApp.config['DNA']['v'] = str(fake_read)
        with open('config.ini', 'w') as configfile:
            ShowcaseApp.config.write(configfile)

        blank_read = float(ShowcaseApp.config['DNA']['g'])
        self.plot = PointPlot(color=[1, 1, 1, 1])
        self.root.ids.sm.get_screen('Standard Table').ids.plot_dna.remove_plot(self.plot)
        self.plot.points = [(x, ((fake_read - blank_read)/500*x+blank_read)) for x in range(0,500)]
        self.root.ids.sm.get_screen('Standard Table').ids.plot_dna.add_plot(self.plot)
        #self.root.ids['plot_dna'].add_plot(self.plot)
        self.pop_up.dismiss()
        
    def DNA_calculate_thread(self):
        fake_read = 0
        '''
        bar = 0
        for i in range(10):
            bar = bar + 10
            self.pop_up.set_bar(bar)
            time.sleep(0.2)
            
        fake_read = 459.40                          #reading RFU
        '''
        try:
            pro_bar = 0
            gain_input = float(self.adc_gain)
            sample_rate_input = float(self.sample_rate)
            ads = ADS.ADS1115(self.i2c,gain=gain_input , data_rate=sample_rate_input, address=0x48)
            chan1sum = 0
            chan2sum = 0
            chan3sum = 0
            chan1 = AnalogIn(ads, ADS.P1)
            chan2 = AnalogIn(ads, ADS.P2)
            chan3 = AnalogIn(ads, ADS.P3)
           
            for i in range(10):
                self.leds[1] = (65535, 65535, 65535)
                self.leds.show()
                time.sleep(0.3)
                chan1read = chan1.value
                chan2read = chan2.value
                chan3read = chan3.value
                chan1sum = chan1sum + chan1read
                chan2sum = chan2sum + chan2read
                chan3sum = chan3sum + chan3read
                #print(str(chan3read) +" "+str(chan2read) +" "+ str(chan1read))
                self.leds[1] = (0, 0, 0)
                self.leds.show()
                time.sleep(0.3)
                pro_bar += 10
                self.pop_up.set_bar(pro_bar)
            #print("result blink: ")
            #print(str(chan3sum/10)+" "+str(chan2sum/10)+" "+str(chan1sum/10))
            self.flo_read[0] = str(chan3sum/10)
            self.flo_read[1] = str(chan2sum/10)
            self.flo_read[2] = str(chan1sum/10)
            fake_read = chan1sum/10
            
        except:
            self.pop_up.dismiss()
            print('read tube failed')
        print(fake_read)
            
        k = float(ShowcaseApp.config['DNA']['k'])
        g = float(ShowcaseApp.config['DNA']['g'])   #blank RFU
        #r = float(ShowcaseApp.config['DNA']['r'])  
        n = float(ShowcaseApp.config['DNA']['n'])   
        v = float(ShowcaseApp.config['DNA']['v'])   #high_end RFU
        s = float(ShowcaseApp.config['DNA']['s'])   #high_standard_con
        
        
        r = (v-g)*((pow(s,n)+k)/pow(s,n))
        result = pow(k*(fake_read - g)/(r-(fake_read-g)), 1/n)
        print(result)
        self.DNA_result = '{:.2f}'.format(result)
        #self.root.ids.sm.get_screen('DNA Result').ids.DNA_result.text = str(result)
            
        self.pop_up.dismiss()
        
    def read_standard_1(self):
        self.show_popup()
        self.go_screen('Standard 1')
        mythread = threading.Thread(target=self.read_standard_1_thread)
        mythread.start()
        
        
    def read_standard_2(self):
        self.show_popup()
        self.go_screen('Standard Table')
        mythread = threading.Thread(target=self.read_standard_2_thread)
        mythread.start()
        
        
    def read_tube(self):
        self.show_popup()
        
        mythread = threading.Thread(target=self.DNA_calculate_thread)
        mythread.start()
        self.go_screen('DNA Result')
        
        
      
        
if __name__ == '__main__':
    ShowcaseApp().run()
