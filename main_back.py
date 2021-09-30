import board
import busio
import os

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
    '''
    def __init__(self, **args):
        #Clock.schedule_once(self.init_widget, 0)
        return super(ShowcaseScreen, self).__init__(**args)

    def update_file_list_entry(self, file_chooser, file_list_entry, *args):
        file_list_entry.children[0].color = (0.0, 0.0, 0.0, 1.0)  # File Names
        file_list_entry.children[1].color = (0.0, 0.0, 0.0, 1.0)  # Dir Names`
    '''
class Exportdata(Screen):    
    def selected(self, filename):
        print(filename)
        
class ShowcaseApp(App):
    #kivy properties
    brightness = StringProperty()
    flo_read = ListProperty([0,0,0])
    gap_read = ListProperty([0,0,0])
    hierarchy_index = ListProperty([])
    DNA_result = StringProperty()
    
    adc_gain = StringProperty()
    sample_rate = StringProperty()
    flo_delay_time = StringProperty()
    led_current = StringProperty()
    sample_times = StringProperty()
    
    record_name = StringProperty('not record')
    #config
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    #brightness =config['BASIC']['brightness']
    led_red_on = False
    led_blue_on = False
    adc_gain = '1'
    sample_rate = '8'
    flo_delay_time = '0.01'
    led_current = '127'
    sample_times = '5'
    #unit = NumericProperty(1)
    home_screen = Builder.load_file("./kv/home.kv")
    setting_screen = Builder.load_file("./kv/settings.kv")
    
    f_record = False
    name = ''
    try:
        spi = busio.SPI(board.SCK, MOSI=board.MOSI)
        
    except:
        print('>>>>>>>>>>>>>>>spi init failed<<<<<<<<<<<<<<<<<<<')
    try:        
        leds = adafruit_tlc59711.TLC59711(spi, auto_show=False)
        leds[0] = (0, 0, 0)
        leds[1] = (0, 0, 0)
        leds.show()
        print('blue bc:')
        print(leds._bcb)
        print('red bc')
        print(leds._bcr)
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
        Window.size = (480, 800)
        
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
            time.sleep(0.1)
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
        ads = ADS.ADS1115(self.i2c,gain=16 , data_rate=16, address=0x48)
        #self.leds[0] = (65535, 65535, 65535)
        #self.leds.show()
        chan2 = AnalogIn(ads, ADS.P2)
     
        for i in range(30):
            print(time.ctime())
            for i in range(5):
                refread_led_off = chan2.value
                print(refread_led_off)
                self.leds[0] = (65535, 65535, 65535)
                self.leds.show()
                time.sleep(0.1)
                refread_led_on = chan2.value
                print(refread_led_on)
                self.leds[0] = (0,0,0)
                self.leds.show()
                time.sleep(0.05)
                print(refread_led_on - refread_led_off)
                print('------------------')
            print('-----------------------30s--------------------')    
            time.sleep(30)
           
        self.leds[1] = (0,0,0)
        self.leds.show()
        
    def time_test_flo(self):
        chan_dark = [0, 0]
        chan_read =  [0, 0]    
        ads = ADS.ADS1115(self.i2c,gain=1 , data_rate=16, address=0x48)
        self.leds._bcr = 64
        print("LED current")
        print(self.leds._bcr)
        chan1 = AnalogIn(ads, ADS.P1)
        #chan2 = AnalogIn(ads, ADS.P2)
        chan3 = AnalogIn(ads, ADS.P3)
        print(time.ctime())
        
        for i in range(2000):
            time.sleep(0.01) #delay
            chan_dark[0] = chan1.value #read off
            chan_dark[1] = chan3.value
             
            self.leds[1] = (65535, 65535, 65535)
            self.leds.show() #led on
            time.sleep(0.01) #delay
            chan_read[0] = chan1.value #read on
            chan_read[1] = chan3.value
            self.leds[1] = (0, 0, 0)
            self.leds.show() #led off
            print(str(chan_dark[1]) + " " + str(chan_read[1]) + " " + str(chan_dark[0]) + " " + str(chan_read[0])) 
            
        print('--------end----------')
        print(time.ctime())   
            
           
        self.leds[1] = (0,0,0)
        self.leds.show()

    def time_test_flo_always_on(self):
        chan_dark = [0, 0]
        chan_read =  [0, 0]    
        ads = ADS.ADS1115(self.i2c,gain=1 , data_rate=16, address=0x48)
        self.leds._bcr = 64
        print("LED current")
        print(self.leds._bcr)
        chan1 = AnalogIn(ads, ADS.P1)
        #chan2 = AnalogIn(ads, ADS.P2)
        chan3 = AnalogIn(ads, ADS.P3)
        print(time.ctime())
        print('--------led off----------')
        chan_dark[0] = chan1.value #read off
        chan_dark[1] = chan3.value
        print(str(chan_dark[1]) + " " + str(chan_dark[0]))
        
        time.sleep(0.01) #delay
        self.leds[1] = (65535, 65535, 65535)
        self.leds.show() #led on
        time.sleep(0.01) #delay
        print('--------begin----------')
        for i in range(2000):
            
            
            chan_read[0] = chan1.value #read on
            chan_read[1] = chan3.value
            time.sleep(0.01) #delay
            print(str(chan_read[1]) + " " + str(chan_read[0]))
            
        self.leds[1] = (0, 0, 0)
        self.leds.show() #led off    
        print('--------end----------')
        print(time.ctime())   
            
           
        self.leds[1] = (0,0,0)
        self.leds.show()        
#-----------------------------Fluorometer---------------------------------
    def show_popup(self):
        self.pop_up = Factory.PopupBox()
        self.pop_up.update_pop_up_text('Reading...')
        self.pop_up.open()        
       
            
    def adc_aver_thread(self): #No Led
        chan0min = 32767
        chan0max = 0
        refmin = 32767
        refmax = 0
        chan1min = 32767
        chan1max = 0
        chanread = [0,0]
        chansum = [0, 0, 0]
        gap = [0, 0, 0]
        try:
            pro_bar = 0
            gain_input = float(self.adc_gain)
            sample_rate_input = float(self.sample_rate)
            ads = ADS.ADS1115(self.i2c,gain=gain_input , data_rate=sample_rate_input, address=0x48)
            chan1 = AnalogIn(ads, ADS.P1)
            chan2 = AnalogIn(ads, ADS.P2)
            chan3 = AnalogIn(ads, ADS.P3)
            
            for i in range(10):
                chanread[0] = chan1.value
                refread = chan2.value
                chanread[1] = chan3.value
                
                if chan0min > chanread[0]:
                    chan0min = chanread[0]
                if chan0max < chanread[0]:
                    chan0max = chanread[0]
                    
                if refmin > refread:
                    refmin = refread
                if refmax < refread:
                    refmax = refread
                    
                if chan1min > chanread[1]:
                    chan1min = chanread[1]
                if chan1max < chanread[1]:
                    chan1max = chanread[1]

                
                chansum[0] = chansum[0] + chanread[0]
                chansum[1] = chansum[1] + refread
                chansum[2] = chansum[2] + chanread[1]
                print(str(chanread[1]) +" "+str(refread) +" "+ str(chanread[0]))
                pro_bar += 10
                self.pop_up.set_bar(pro_bar)
                
            print('ADC average: ')
            print(str(chansum[2]/10)+" "+str(chansum[1]/10)+" "+str(chansum[0]/10))
            self.flo_read[0] = str(chansum[2]/10)
            self.flo_read[1] = str(chansum[1]/10)
            self.flo_read[2] = str(chansum[0]/10)

            gap[0] = chan0max - chan0min
            gap_ref = refmax - refmin
            gap[1] = chan1max - chan1min
            
            print('Gap:')
            print(str(chan0max)+" "+str(chan1max)+" "+str(refmax))
            print(str(chan0min)+" "+str(chan1min)+" "+str(refmin))
            print(str(gap[0])+" "+str(gap[1])+" "+str(gap[0]))
            print('------------------')
            self.gap_read[0] = str(gap[0])
            self.gap_read[1] = str(gap[1])
            self.gap_read[2] = str(gap[2])
            
            self.pop_up.dismiss()
        except:
            self.pop_up.dismiss()
            print('ADC average test failed')
           
    def adc_aver_with_led_thread(self): #LED always on mode
        chan0min = 32767
        chan0max = 0
        refmin = 32767
        refmax = 0 
        chan1min = 32767
        chan1max = 0
        
        chan_gap = [0, 0]
        chan_dark = [0, 0]
        chan_light = [0, 0]
        chan_result = [0, 0]
        chan_sum = [0, 0]
        ref_sum = 0
        
        
        delay_time = float(self.flo_delay_time)
        gain_input = float(self.adc_gain)
        sample_rate_input = float(self.sample_rate)
        self.leds._bcr = int(self.led_current)
        s_times = int(self.sample_times)
        
        if self.f_record:
            flo_record = open(self.name, "a")
            
        try:
            ads = ADS.ADS1115(self.i2c,gain=gain_input , data_rate=sample_rate_input, address=0x48)
            print('')
            print('')
            print('No blink test')
            print("-----------delay time [" + str(delay_time) + "] current [" + str(self.leds._bcr) + "] ------------\n")    
            if self.f_record:
                flo_record.write('\n')
                flo_record.write('\n')
                flo_record.write('No blink test\n')
                flo_record.write("-----------delay time [" + str(delay_time) + "] current [" + str(self.leds._bcr) + "] ------------\n")
                    
            pro_bar = 0
           
            

            
            chan0 = AnalogIn(ads, ADS.P3)
            chanref = AnalogIn(ads, ADS.P2)
            chan1 = AnalogIn(ads, ADS.P1)

            chan_dark[0] = chan0.value
            ref_dark = chanref.value
            chan_dark[1] = chan1.value

            
            
            
            self.leds[1] = (65535, 65535, 65535) #led on
            self.leds.show()
            time.sleep(delay_time) #delay
            
            for i in range(s_times):
                chan_light[0] = chan0.value
                ref_light = chanref.value
                chan_light[1] = chan1.value

                if chan0min > chan_light[0]:
                    chan0min = chan_light[0]
                if chan0max < chan_light[0]:
                    chan0max = chan_light[0]
                  
                if refmin > ref_light:
                    refmin = ref_light
                if refmax < ref_light:
                    refmax = ref_light
                        
                if chan1min > chan_light[1]:
                    chan1min = chan_light[1]
                if chan1max < chan_light[1]:
                    chan1max = chan_light[1]    
                
                chan_sum[0] = chan_sum[0] + chan_light[0]
                chan_sum[1] = chan_sum[1] + chan_light[1]
                ref_sum = ref_sum + ref_light
                
                print(str(chan_dark[0]) + " " + str(chan_light[0]) + " " + \
                      str(chan_dark[1]) + " " + str(chan_light[1]) + " " + \
                      str(ref_dark) + " " + str(ref_light))
                
                if self.f_record:
                    flo_record.write(str(chan_dark[0]) +" "+str(chan_light[0]) +" "+ \
                                     str(chan_dark[1]) +" "+str(chan_light[1]) +" "+ \
                                     str(ref_dark) + " " + str(ref_light) + "\n")                

                pro_bar += 100/s_times
                self.pop_up.set_bar(pro_bar)

            self.leds[1] = (0, 0, 0) #led off
            self.leds.show()    

            
            chan_result[0] = chan_sum[0]/s_times - chan_dark[0] 
            chan_result[1] = chan_sum[1]/s_times - chan_dark[1]
            ref_result = ref_sum/s_times - ref_dark
            
            #show result
            chan_result[0] = round(chan_result[0], 1)
            chan_result[1] = round(chan_result[1], 1)
            ref_result = round(ref_result, 1)
            
            print("result led no blink: ")
            print('Dark: ' + str(chan_dark[0]) + " " + str(chan_dark[1]) + " " + str(ref_dark))
            print('Aver: ' + str(chan_sum[0]/s_times)+ " " +str(chan_sum[1]/s_times) + " " +str(ref_sum/s_times))
            print('Sub: ' + str(chan_result[0])+ " " +str(chan_result[1]) + " " +str(ref_result))
            print('------------------------')

            if self.f_record:
                flo_record.write("result led no blink: \n")
                flo_record.write('Dark: ' + str(chan_dark[0]) + " " + str(chan_dark[1]) + " " + str(ref_dark) + "\n")
                flo_record.write('Aver: ' + str(chan_sum[0]/s_times)+ " " +str(chan_sum[1]/s_times) + " " +str(ref_sum/s_times) + "\n")
                flo_record.write('Sub: ' + str(chan_result[0])+ " " +str(chan_result[1]) + " " +str(ref_result) + "\n")
                flo_record.write('---------------------------------------------------------------------------------------------------------------------------\n')
                
            self.flo_read[0] = str(chan_result[0])
            self.flo_read[1] = str(ref_result)
            self.flo_read[2] = str(chan_result[1])

            chan_gap[0] = chan0max - chan0min
            chan_gap[1] = chan1max - chan1min
            ref_gap = refmax - refmin
            
            print('Gap:')
            print('Max: ' + str(chan0max) + " " + str(chan1max) + " " + str(refmax))
            print('Min: ' + str(chan0min) + " " + str(chan1min) + " " + str(refmin))
            print('Result: ' + str(chan_gap[0]) + " " +str(chan_gap[1]) + " " + str(ref_gap))
            print('------------------------------------------------------------------------------')
            self.gap_read[0] = str(chan_gap[0])
            self.gap_read[1] = str(ref_gap)
            self.gap_read[2] = str(chan_gap[1])
            
            self.pop_up.dismiss()
            
        except:
            self.pop_up.dismiss()
            print('ADC average led no blink failed')
    

    def adc_aver_with_blink_sub_gaincontrol_thread(self):
        gainrange = [1, 2, 4, 8, 16]
        chan0min = 32767
        chan0max = 0
        refmin = 32767
        refmax = 0 
        chan1min = 32767
        chan1max = 0

        
        chan_gap = [0, 0]
        chan_dark = [0, 0]
        chan_light = [0, 0]
        chan_sub = [0, 0]
        chan_result = [0, 0]
        chan_sum = [0, 0]
        ref_sum = 0
        
        delay_time = float(self.flo_delay_time)
        gain_input = float(self.adc_gain)
        sample_rate_input = float(self.sample_rate)
        self.leds._bcr = int(self.led_current)
        s_times = int(self.sample_times)
        
        if self.f_record:
            flo_record = open(self.name, "a")
        try:
            pro_bar = 0
            ads = ADS.ADS1115(self.i2c,gain=gain_input , data_rate=sample_rate_input, address=0x48)
            chan0 = AnalogIn(ads, ADS.P3)
            chanref = AnalogIn(ads, ADS.P2)
            chan1 = AnalogIn(ads, ADS.P1)
            
            #--------------------------first read------------------
            for ap in gainrange:
                pass_flag = True
                print('')
                print('')
                print("-----------start over with amplify [" + str(ap) + "] gain [" + str(gain_input) + "]--------------")
                print("-----------delay time [" + str(delay_time) + "] current [" + str(self.leds._bcr) + "] ------------\n")
                
                if self.f_record:
                    flo_record.write('\n')
                    flo_record.write('\n')
                    flo_record.write('Blink test\n')
                    flo_record.write("-----------start over with amplify [" + str(ap) + "] gain [" + str(gain_input) + "]--------------\n")
                    flo_record.write("-----------delay time [" + str(delay_time) + "] current [" + str(self.leds._bcr) + "] ------------\n")
                    
                chan_dark[0] = chan0.value
                ref_dark = chanref.value
                chan_dark[1] = chan1.value
                    
                self.leds[1] = (65535, 65535, 65535)
                self.leds.show() #led first on
                time.sleep(delay_time) #delay

                chan_light[0] = chan0.value
                ref_light = chanref.value
                chan_light[1] = chan1.value

                for read in chan_light:
                    if (read > 25000):
                        print("-------reach max, reducing gain-------")
                        if self.f_record:
                            flo_record.write("-------reach max, reducing gain-------\n")
                        gain_input = gain_input/2

                        
                        if (gain_input < 1):
                            print('reach minimal gain, abort')
                            if self.f_record:
                                flo_record.write('reach minimal gain, abort\n')
                            self.pop_up.dismiss()
                            return
                       
                        self.leds[1] = (0, 0, 0)
                        self.leds.show() #led reset off
                        time.sleep(delay_time) #delay
                        ads = ADS.ADS1115(self.i2c, gain=gain_input , data_rate=sample_rate_input, address=0x48)
                        chan0 = AnalogIn(ads, ADS.P3)
                        chanref = AnalogIn(ads, ADS.P2)
                        chan1 = AnalogIn(ads, ADS.P1)
                        pass_flag = False
                        break

                if pass_flag:
                    break

            
            
            chan_sub[0] = (chan_light[0] - chan_dark[0]) * ap
            chan_sub[1] = (chan_light[1] - chan_dark[1]) * ap
            ref_sub = (ref_light - ref_dark) * ap
            
            if chan0min > chan_sub[0]:
                chan0min = chan_sub[0]
            if chan0max < chan_sub[0]:
                chan0max = chan_sub[0]
                
                    
            if chan1min > chan_sub[1]:
                chan1min = chan_sub[1]
            if chan1max < chan_sub[1]:
                chan1max = chan_sub[1]

            if refmin > ref_sub:
                refmin = ref_sub
            if refmax < ref_sub:
                refmax = ref_sub    
            
            chan_sum[0] = chan_sum[0] + chan_sub[0]
            chan_sum[1] = chan_sum[1] + chan_sub[1]
            ref_sum = ref_sum + ref_sub
       
            print(str(chan_dark[0]) +" "+str(chan_light[0]) +" "+ str(chan_sub[0]) + "  " + \
                  str(chan_dark[1]) +" "+str(chan_light[1]) +" "+ str(chan_sub[1]) + "  " + \
                  str(ref_dark) + " " + str(ref_light) + " " + str(ref_sub))
            
            if self.f_record:
                flo_record.write(str(chan_dark[0]) +" "+str(chan_light[0]) +" "+ str(chan_sub[0]) + "  " + \
                                 str(chan_dark[1]) +" "+str(chan_light[1]) +" "+ str(chan_sub[1]) + "  " + \
                                 str(ref_dark) + " " + str(ref_light) + " " + str(ref_sub) + "\n")

                
            self.leds[1] = (0, 0, 0)
            self.leds.show() #led first off
            pro_bar += 100/s_times
            self.pop_up.set_bar(pro_bar)
            time.sleep(delay_time) #delay
            
            
            #-------------------------read else 9----------------------
            for i in range(s_times - 1):
                chan_dark[0] = chan0.value
                ref_dark = chanref.value
                chan_dark[1] = chan1.value
             
                self.leds[1] = (65535, 65535, 65535)
                self.leds.show() #led loop on
                time.sleep(delay_time) #delay

                chan_light[0] = chan0.value
                ref_light = chanref.value
                chan_light[1] = chan1.value
        
                chan_sub[0] = (chan_light[0] - chan_dark[0]) * ap
                ref_sub = (ref_light - ref_dark) * ap
                chan_sub[1] = (chan_light[1] - chan_dark[1]) * ap

                if chan0min > chan_sub[0]:
                    chan0min = chan_sub[0]
                if chan0max < chan_sub[0]:
                    chan0max = chan_sub[0]
                    
                    
                if chan1min > chan_sub[1]:
                    chan1min = chan_sub[1]
                if chan1max < chan_sub[1]:
                    chan1max = chan_sub[1]

                if refmin > ref_sub:
                    refmin = ref_sub
                if refmax < ref_sub:
                    refmax = ref_sub
                        
                chan_sum[0] = chan_sum[0] + chan_sub[0]
                ref_sum = ref_sum + ref_sub
                chan_sum[1] = chan_sum[1] + chan_sub[1]

                print(str(chan_dark[0]) +" "+str(chan_light[0]) +" "+ str(chan_sub[0]) + "  " + \
                      str(chan_dark[1]) +" "+str(chan_light[1]) +" "+ str(chan_sub[1]) + "  " + \
                      str(ref_dark) + " " + str(ref_light) + " " + str(ref_sub))
                
                
                if self.f_record:
                    flo_record.write(str(chan_dark[0]) +" "+str(chan_light[0]) +" "+ str(chan_sub[0]) + "  " + \
                                     str(chan_dark[1]) +" "+str(chan_light[1]) +" "+ str(chan_sub[1]) + "  " + \
                                     str(ref_dark) + " " + str(ref_light) + " " + str(ref_sub) + "\n")
                    
                self.leds[1] = (0, 0, 0)
                self.leds.show() #led loop off
                time.sleep(delay_time) #delay
                pro_bar += 100/s_times
                self.pop_up.set_bar(pro_bar)
                
            print("result blink sub with gain control: ")
            
            chan_result[0] = chan_sum[0]/s_times
            chan_result[1] = chan_sum[1]/s_times
            ref_result = ref_sum/s_times
            
            chan_result[0] = round(chan_result[0], 1)
            chan_result[1] = round(chan_result[1], 1)
            ref_result = round(ref_result, 1)
            
            print(str(chan_result[0])+ " " +str(chan_result[1]) + " " + str(ref_result))
            
            if self.f_record:
                flo_record.write("result blink sub with gain control: \n")
                flo_record.write(str(chan_result[0])+ " " +str(chan_result[1]) + " " + str(ref_result) + "\n")
                flo_record.write('---------------------------------------------------------------------------------------------------------------------------\n')

            self.flo_read[0] = str(chan_result[0])
            self.flo_read[1] = str(ref_result)
            self.flo_read[2] = str(chan_result[1])

            chan_gap[0] = chan0max - chan0min
            ref_gap = refmax - refmin
            chan_gap[1] = chan1max - chan1min
            
            print('Gap:')
            print('Max: ' + str(chan0max) + " " + str(chan1max) + " " + str(refmax))
            print('Min: ' + str(chan0min) + " " + str(chan1min) + " " + str(refmin))
            print('Result: ' + str(chan_gap[0]) + " " +str(chan_gap[1]) + " " + str(ref_gap))
            print('------------------------------------------------------------------------------')
            self.gap_read[0] = str(chan_gap[0])
            self.gap_read[1] = str(ref_gap)
            self.gap_read[2] = str(chan_gap[1])
            
            ads = ADS.ADS1115(self.i2c,gain=float(self.adc_gain) , data_rate=sample_rate_input, address=0x48)
            if self.f_record:
                flo_record.close()
            self.pop_up.dismiss()
        
        except:
            self.pop_up.dismiss()
            if self.f_record:
                flo_record.write('ADC average blink sub with gain control failed\n')
            print('ADC average blink sub with gain control failed')
        
            
    def read_led_current_thread(self):
        try:
            pro_bar = 0
            gain_input = float(self.adc_gain)
            sample_rate_input = float(self.sample_rate)
            ads = ADS.ADS1115(self.i2c,gain=gain_input , data_rate=sample_rate_input, address=0x48)
            #chan1sum = 0
            #chan2sum = 0
            #chan3sum = 0
            chan1 = AnalogIn(ads, ADS.P1)
            chan2 = AnalogIn(ads, ADS.P2)
            chan3 = AnalogIn(ads, ADS.P3)
            print('')
            
            self.leds[1] = (65535, 65535, 65535)
            
            for i in range(128):                
                self.leds._bcr = i
                self.leds.show()
                time.sleep(0.01)
                #print("bc value " + str(self.leds._bcr))
                chan1read2 = chan1.value
                chan2read2 = chan2.value
                chan3read2 = chan3.value
                print(str(self.leds._bcr) + ": " + str(chan3read2) +" "+str(chan2read2) +" "+ str(chan1read2))

             
                #self.leds[1] = (0, 0, 0)
                #self.leds.show()
                #time.sleep(0.1)
                pro_bar += 100/128
                self.pop_up.set_bar(pro_bar)
                
            print('------------------------')
            self.leds._bcr = 127
            self.leds[1] = (0, 0, 0)
            self.leds.show()
            self.pop_up.dismiss()
        except:
            self.pop_up.dismiss()
            print('LED Current test failed')
            
    def adc_aver(self):
        self.show_popup()
        mythread = threading.Thread(target=self.adc_aver_thread)
        mythread.start()
        
    def adc_aver_with_led(self):
        self.show_popup()
        mythread = threading.Thread(target=self.adc_aver_with_led_thread)
        mythread.start()
    """    
    def adc_aver_with_blink(self):
        self.show_popup()
        mythread = threading.Thread(target=self.adc_aver_with_blink_thread)
        mythread.start()

    def adc_aver_with_blink_sub(self):
        self.show_popup()
        mythread = threading.Thread(target=self.adc_aver_with_blink_sub_thread)
        mythread.start()
    """    


    def adc_aver_with_blink_sub_gaincontrol(self):
        self.show_popup()
        mythread = threading.Thread(target=self.adc_aver_with_blink_sub_gaincontrol_thread)
        mythread.start()
        
    def read_led_current(self):
        self.show_popup()
        mythread = threading.Thread(target=self.read_led_current_thread)
        mythread.start()
        
    def create_fluorometer_record(self):
        t = time.localtime()
        self.name = time.strftime("%Y_%m_%d_%H_%M",t)
        self.record_name = self.name
        self.name = 'home/pi/Fluorometer/Records/' + self.name + '.txt'
        self.f_record = True
        flo_record = open(self.name, "w")

    def export_to_usb(self):
        try:
            os.system("mount /dev/sda1 /mnt")
            os.system("cp -r home/pi/Fluorometer/Records/ /mnt/")
            time.sleep(3)
            os.system("sudo umount /mnt")
        except:
            print("export USB failed")
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
