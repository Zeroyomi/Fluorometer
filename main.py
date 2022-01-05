# import board
# import busio
# import os

import time, threading
import configparser

from pathlib import Path

from kivy.app import App

from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, \
    ListProperty, ObjectProperty
from kivy.clock import Clock

from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.label import Label
from kivy.core.window import Window

from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.storage.jsonstore import JsonStore  # test
import json
import csv

# for popup
from kivy.factory import Factory
from kivy.uix.popup import Popup

# for table
# from kivy_garden.graph import Graph, MeshLinePlot, SmoothLinePlot, MeshStemPlot, PointPlot, ScatterPlot
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt


# hardware
# import adafruit_tlc59711
# import adafruit_ads1x15.ads1115 as ADS
# from adafruit_ads1x15.analog_in import AnalogIn


class PopupBox(Popup):
    pop_up_text = ObjectProperty()

    def update_pop_up_text(self, p_message):
        self.pop_up_text.text = p_message

    def set_bar(self, value):
        self.reading_progress_bar.value = value


class WindowManager(ScreenManager):
    pass


class MainScreen(Screen):
    pass


class ShowcaseScreen(Screen):
    # fullscreen = BooleanProperty(False)

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


usb_path = ''
export_group = []
fig = ''

class Exportdata(Screen):
    @staticmethod
    def selected(filename):
        # print(filename)
        global usb_path
        usb_path = str(filename)

    @staticmethod
    def delete(filename):
        try:
            os.remove(filename[0])
        except:
            print('error when delete')


class DataRead(Screen):
    pass


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, BoxLayout):
    """ Add selection support to the Label """
    Time = StringProperty('')
    Assay = StringProperty('')
    Concentration = StringProperty('')

    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        global export_group
        if is_selected:
            export_group.append(index)
            print(export_group)
            # print("selection changed to {0}".format(rv.data[index]))
        else:
            if index in export_group:
                export_group.remove(index)
                print(export_group)
            else:
                pass
            # print("selection removed for {0}".format(rv.data[index]))


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        # self.data = [{'text': str(x)} for x in range(10)]

    def clear_all(self, rv):
        global export_group
        export_group = []
        for i in range(len(self.view_adapter.views)):
            # self.view_adapter.views[i].selected = False
            self.view_adapter.views[i].parent.clear_selection()


class DataRead2(Screen):
    @staticmethod
    def export_selection(rv):
        global export_group
        # for index in export_group:
        # print(rv.data[index].values())
        global usb_path
        usb_path = usb_path[2:-2]
        print(usb_path)
        f = open(usb_path)
        j_data = json.load(f)
        f.close()

        if os.path.exists('/home/pi/Fluorometer/Records/temp.csv'):
            os.remove('/home/pi/Fluorometer/Records/temp.csv')

        temp_csv = open('/home/pi/Fluorometer/Records/temp.csv', 'w+', encoding='utf-8')
        csv_writer = csv.writer(temp_csv)
        count = 0
        print(export_group)
        j_len = len(j_data)
        for test in j_data:
            print('count:')
            print(count)
            if count == 0:
                # csv_writer.writerow(rv.data[index].keys())
                header = j_data[test].keys()
                csv_writer.writerow(header)

            # csv_writer.writerow(rv.data[index].values())
            true_index = j_len - 1 - count
            if true_index in export_group:
                print(j_data[test].values())
                export_group.remove(true_index)
                csv_writer.writerow(j_data[test].values())
            print(export_group)
            count += 1

        temp_csv.close()

        csv_name = 'OmecData_' + time.strftime('%Y' + '_' + '%m' + '_' + '%d' + '_' + '%H' + '%M' + '%S') + '.csv'
        print("file name is: " + csv_name)
        # os.rename('/home/pi/Fluorometer/Records/temp.csv', '/home/pi/Fluorometer/Records/' +csv_name)
        os.system("cp /home/pi/Fluorometer/Records/temp.csv /home/pi/Fluorometer/Records/{0}".format(csv_name))

        # csv_name = csv_name.replace(':','\:') #do before CP
        # command = "cp " + usb_path + " /mnt/"
        command = "cp /home/pi/Fluorometer/Records/{0} /mnt/".format(csv_name)
        print("copy command is: " + command)

        os.system("mount /dev/sda1 /mnt")
        os.system(command)  # os.system("cp -r home/pi/Fluorometer/Records/ /mnt/")
        time.sleep(3)
        os.system("sudo umount /mnt")
        os.remove('/home/pi/Fluorometer/Records/{0}'.format(csv_name))


class FluorometerApp(App):
    # kivy properties
    brightness = StringProperty()
    flo_read = ListProperty([0, 0, 0])
    gap_read = ListProperty([0, 0, 0])
    hierarchy_index = ListProperty([])
    DNA_result = StringProperty()
    DNA_result_real = StringProperty()
    DNA_type = StringProperty()
    DNA_standard_1 = StringProperty()
    DNA_standard_2 = StringProperty()
    DNA_last_read_1 = StringProperty()
    DNA_last_read_2 = StringProperty()
    DNA_volume = NumericProperty(1)
    DNA_unit = StringProperty("ng/μL")

    Fluorometer_type = StringProperty()

    adc_gain = StringProperty()
    sample_rate = StringProperty()
    flo_delay_time = StringProperty()
    led_current = StringProperty()
    sample_times = StringProperty()
    clock_time = StringProperty(0)
    title_name = StringProperty('home')
    # data_read_content = StringProperty()
    record_name = StringProperty('not record')
    # config
    config = configparser.ConfigParser()
    config.read('/home/pi/Fluorometer/config.ini')

    # brightness =config['BASIC']['brightness']
    led_red_on = False
    led_blue_on = False
    adc_gain = '1'
    sample_rate = '8'
    flo_delay_time = '0.01'
    led_current = '127'
    sample_times = '5'
    unit = NumericProperty(1)


    f_record = False

    path_dir = "/home/pi/Fluorometer/Records/"

    # Directory
    # directory ='Fluorometer ' + str(time.strftime("%Y_%m_%d",t))
    # Parent Directory path
    # parent_dir = "/home/pi/Fluorometer/Records/"

    # Path
    # path = os.path.join(parent_dir, directory)

    # Create the directory
    # os.mkdir(path)

    try:
        spi = busio.SPI(board.SCK, MOSI=board.MOSI)

    except:
        print('>>>>>>>>>>>>>>>spi init failed<<<<<<<<<<<<<<<<<<<')
    try:
        leds = adafruit_tlc59711.TLC59711(spi, auto_show=False)
        leds[0] = (0, 0, 0)
        leds[1] = (0, 0, 0)
        leds.show()
        # print('blue bc:')
        # print(leds._bcb)
        # print('red bc')
        # print(leds._bcr)
    except:
        print('>>>>>>>>>>>>>>>led init failed<<<<<<<<<<<<<<<<<<<')

    try:
        i2c = busio.I2C(board.SCL, board.SDA)
    except:
        print('>>>>>>>>>>>>>>>i2c init failed<<<<<<<<<<<<<<<<<<<')
    # try:
    # ads = ADS.ADS1115(i2c, gain=adc_gain, data_rate=sample_rate, address=0x48)
    # except:
    # print('>>>>>>>>>>>>>>>ads init failed<<<<<<<<<<<<<<<<<<<')

    try:
        file = open("/sys/class/backlight/rpi_backlight/brightness", "r")
        brightness = file.read()
        file.close()
    except:
        print('>>>>>>>>>>>>>>>Brightness init error<<<<<<<<<<<<<<<<<<<<<<<')

    def build(self):
        self.setup_localizer()
        self.main_screen = Builder.load_file('./kv/main.kv')
        self.home_screen = Builder.load_file("./kv/home.kv")
        self.setting_screen = Builder.load_file("./kv/settings.kv")
        self.root = self.main_screen
        self.title = 'Fluorometer'
        Window.size = (480, 800)

        self.hierarchy_index.append('home')
        print(self.hierarchy_index)
        # print(self.root)
        # print(self.root.get_screen('mainscreen').ids)
        self.root.get_screen('mainscreen').ids.sm.switch_to(self.home_screen, direction='right')
        # screen = Builder.load_file("./kv/home.kv")
        # self.ids.sm.current = 'Home'
        # self.root.ids.sm.switch_to(self.home_screen, direction='right')
        # self.root.ids.main_label.text = 'Choose an assay'
        # self.root.ids.back_btn.disabled=True

        # app_clock = App_clock()
        Clock.schedule_interval(self.clock_update, 1)
        # return app_clock
        self.DNA_last_read_1 = str(FluorometerApp.config['AccuGreen']['g'])
        self.DNA_last_read_2 = str(FluorometerApp.config['AccuGreen']['v'])

    @staticmethod
    def setup_localizer():
        from kivy_garden.i18n.localizer import KXLocalizer, DictBasedTranslator
        translation_table = {
            'data': {
                'en': 'Data',
                'cn': '数据',
            },
            'settings': {
                'en': 'Settings',
                'cn': '设置',
            },
            'language': {
                'en': 'Language',
                'cn': '语言',
            },
            'brightness': {
                'en': 'Brightness',
                'cn': '亮度',
            },
            'home': {
                'en': 'Choose an assay',
                'cn': '选择一种实验',
            },
            'Fluo_1': {
                'en': 'Choose excitation',
                'cn': '选择激发',
            },
            'Instrument': {
                'en': 'Instrument',
                'cn': '仪器设置',
            },
            'Instrument Settings': {
                'en': 'Instrument Settings',
                'cn': '仪器设置',
            },
        }
        KXLocalizer(translator=DictBasedTranslator(translation_table)).install(name='l')

    def clock_update(self, *args):
        self.root.get_screen('mainscreen').ids.app_clock.text = time.strftime(
            '%Y' + '/' + '%m' + '/' + '%d' + '     %H' + ':' + '%M')
        # self.clock_time = time.strftime('%I'+':'+'%M'+' %p')
        # print(self.text)

    def go_home(self):

        if (len(self.hierarchy_index) == 1) and (self.hierarchy_index[0] == 'home'):
            return
        del self.hierarchy_index[:]
        self.hierarchy_index.append('home')
        print(self.hierarchy_index)
        # screen = Builder.load_file("./kv/home.kv")
        self.root.get_screen('mainscreen').ids.sm.switch_to(self.home_screen, direction='right')
        self.title_name = 'home'
        #self.root.get_screen('mainscreen').ids.main_label.text = 'Choose an assay'
        self.root.get_screen('mainscreen').ids.back_btn.disabled = True

    def go_settings(self):
        # if (len(self.hierarchy_index) == 1) and (self.hierarchy_index[0] == 'settings'):
        if self.hierarchy_index[-1] == 'settings':
            return
        # del self.hierarchy_index[:]
        self.hierarchy_index.append('settings')
        print(self.hierarchy_index)

        self.root.get_screen('mainscreen').ids.sm.switch_to(self.setting_screen, direction='right')
        #self.root.get_screen('mainscreen').ids.main_label.text = 'Settings'
        self.title_name = 'Settings'
        self.root.get_screen('mainscreen').ids.back_btn.disabled = False

    def go_screen(self, screen_name):
        if self.hierarchy_index[-1] != screen_name:
            self.hierarchy_index.append('{0}'.format(screen_name))
        print(self.hierarchy_index)
        # self.previous_screen = self.current_screen
        # self.current_screen = screen_name

        screen = self.load_screen(screen_name)

        # sm = self.root.ids.sm
        # sm.switch_to(screen, direction='left')

        self.root.get_screen('mainscreen').ids.sm.switch_to(screen, direction='left')
        #self.root.get_screen('mainscreen').ids.main_label.text = '{0}'.format(screen_name)
        self.title_name = '{0}'.format(screen_name)
        self.root.get_screen('mainscreen').ids.back_btn.disabled = False

    def go_previous(self):
        if len(self.hierarchy_index) == 2:
            if self.hierarchy_index[0] == 'home':
                self.go_home()
                return
            # if self.hierarchy_index[0] == 'settings':
            # self.go_settings()
            # return

        self.hierarchy_index.pop()
        previous_name = self.hierarchy_index[-1]
        print(self.hierarchy_index)
        print('goto ' + previous_name)

        screen = self.load_screen(previous_name)

        # self.root.ids.sm.switch_to(screen, direction='right')
        # self.root.ids.main_label.text = '{0}'.format(previous_name)

        self.root.get_screen('mainscreen').ids.sm.switch_to(screen, direction='right')
        #self.root.get_screen('mainscreen').ids.main_label.text = '{0}'.format(previous_name)
        self.title_name = '{0}'.format(previous_name)

    def load_screen(self, screen_name):
        screen = Builder.load_file("./kv/{0}.kv".format(screen_name))
        return screen

    def load_fluorometer(self):
        try:
            t = time.localtime()
            self.path_dir = "/home/pi/Fluorometer/Records/" + 'Fluorometer ' + str(time.strftime("%Y_%m_%d", t))

            Path(self.path_dir).mkdir(parents=True, exist_ok=True)
            print("Fluorometer Record Create")
            self.record_name = str(time.strftime("%Y_%m_%d", t))
        except:
            print(">>>>>Fluorometer Record Failed<<<<")
            self.record_name = "Folder False"

    def load_DNA(self):

        try:
            self.leds._bcr = 64

            t = time.localtime()
            self.path_dir = "/home/pi/Fluorometer/Records/" + 'DNA ' + str(time.strftime("%Y_%m_%d", t))

            Path(self.path_dir).mkdir(parents=True, exist_ok=True)
            print("DNA Record Create")
        except:
            print(">>>>>DNA Record Failed<<<<")
        # -----------------------------Data---------------------------------

    def go_data(self):
        # del self.hierarchy_index[:]
        self.hierarchy_index.append('data')
        print(self.hierarchy_index)
        # self.root.switch_to(self.data_screen)
        self.root.current = 'dataexport'
        self.root.get_screen('dataexport').ids.filechooser._update_files()

    def data_back(self):
        # del self.hierarchy_index[:]
        self.hierarchy_index.pop()
        # self.hierarchy_index.append('home')
        # self.hierarchy_index.append('Fluorometer_real')
        print(self.hierarchy_index)
        self.root.current = 'mainscreen'

    def data_read(self, path, filename):
        global export_group
        export_group = []
        # del self.hierarchy_index[:]
        try:

            # with open(os.path.join(path, filename[0])) as stream:
            # self.data_read_content = stream.read()
            # self.root.get_screen('dataread2').ids.dataRst.text = self.data_read_content
            # print(self.data_read_content)

            # json_data = JsonStore(filename[0])

            # for test in json_data:
            # print(json_data.get(test))

            f = open(filename[0])
            j_data = json.load(f)

            '''
            self.root.get_screen('dataread2').ids.rec_view.data.insert(0, \
            {'time':'11/10/2021',\
             'assay':'blue',\
             'concentration':'28/ul'})
            '''

            # dataread is old rst read page
            for test in j_data:
                self.root.get_screen('dataread2').ids.rec_view.data.insert(0, {'Time': j_data[test]['Test_Date'],
                                                                               'Assay': j_data[test]['Excitation'],
                                                                               'Concentration': j_data[test][
                                                                                                    'Original_sample'] +
                                                                                                j_data[test][
                                                                                                    'Original_sample_units']})

            f.close()
            self.root.current = 'dataread2'
            self.hierarchy_index.append('read')
            print(self.hierarchy_index)
        except:
            print("can't read empty")

    def read_back(self):
        # del self.hierarchy_index[:]
        # self.hierarchy_index.append('data')
        self.hierarchy_index.pop()
        print(self.hierarchy_index)
        self.root.get_screen('dataread2').ids.rec_view.data = []
        self.root.current = 'dataexport'

    # -----------------------------Settings---------------------------------
    def brightness_control(self, *args):
        self.brightness = str(int(args[1]))
        try:
            file = open("/sys/class/backlight/rpi_backlight/brightness", "w")
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

    '''
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
    '''

    # -----------------------------Fluorometer---------------------------------
    def show_popup(self):
        self.pop_up = Factory.PopupBox()
        self.pop_up.update_pop_up_text('Reading...')
        self.pop_up.open()

    def adc_aver_thread(self):  # No Led
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

        try:
            pro_bar = 0
            ads = ADS.ADS1115(self.i2c, gain=gain_input, data_rate=sample_rate_input, address=0x48)
            chan0 = AnalogIn(ads, ADS.P3)
            chanref = AnalogIn(ads, ADS.P2)
            chan1 = AnalogIn(ads, ADS.P1)

            for i in range(s_times):

                chan_dark[0] = chan0.value
                ref_dark = chanref.value
                chan_dark[1] = chan1.value

                if chan0min > chan_dark[0]:
                    chan0min = chan_dark[0]
                if chan0max < chan_dark[0]:
                    chan0max = chan_dark[0]

                if refmin > ref_dark:
                    refmin = ref_dark
                if refmax < ref_dark:
                    refmax = ref_dark

                if chan1min > chan_dark[1]:
                    chan1min = chan_dark[1]
                if chan1max < chan_dark[1]:
                    chan1max = chan_dark[1]

                chan_sum[0] = chan_sum[0] + chan_dark[0]
                chan_sum[1] = chan_sum[1] + chan_dark[1]
                ref_sum = ref_sum + ref_dark
                print(str(chan_dark[0]) + " " + \
                      str(chan_dark[1]) + " " + \
                      str(ref_dark))

                pro_bar += 100 / s_times
                self.pop_up.set_bar(pro_bar)

            chan_result[0] = chan_sum[0] / s_times
            chan_result[1] = chan_sum[1] / s_times
            ref_result = ref_sum / s_times

            # show result
            chan_result[0] = round(chan_result[0], 1)
            chan_result[1] = round(chan_result[1], 1)
            ref_result = round(ref_result, 1)

            print('Dark average: ')
            print(str(chan_result[0]) + " " + str(chan_result[1]) + " " + str(ref_result))

            self.flo_read[0] = str(chan_result[0])
            self.flo_read[1] = str(ref_result)
            self.flo_read[2] = str(chan_result[1])

            chan_gap[0] = chan0max - chan0min
            chan_gap[1] = chan1max - chan1min
            ref_gap = refmax - refmin

            print('Gap:')
            print('Max: ' + str(chan0max) + " " + str(chan1max) + " " + str(refmax))
            print('Min: ' + str(chan0min) + " " + str(chan1min) + " " + str(refmin))
            print('Result: ' + str(chan_gap[0]) + " " + str(chan_gap[1]) + " " + str(ref_gap))
            print('------------------------------------------------------------------------------')
            self.gap_read[0] = str(chan_gap[0])
            self.gap_read[1] = str(ref_gap)
            self.gap_read[2] = str(chan_gap[1])

            self.pop_up.dismiss()
        except:
            self.pop_up.dismiss()
            print('No LED test failed')

    def adc_aver_with_led_thread(self):  # LED always on mode
        t = time.localtime()
        index_name = 'LED continue ' + str(time.strftime("%H_%M_%S", t))
        # self.name = time.strftime("%Y_%m_%d_%H_%M",t)
        record_name = self.path_dir + '/' + index_name
        # self.name = '/home/pi/Fluorometer/Records/' + self.name + '.txt'
        self.f_record = True
        flo_record = open(record_name, "w")

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
        # comment if auto-record
        # if self.f_record:
        # flo_record = open(self.name, "a")

        try:
            ads = ADS.ADS1115(self.i2c, gain=gain_input, data_rate=sample_rate_input, address=0x48)
            title_name = 'LED continue test ' + str(time.strftime("%Y%m%d_%H%M", t))
            print('')
            print('')
            print(title_name)
            print(
                "-----------delay time [" + str(delay_time) + "] current [" + str(self.leds._bcr) + "] ------------\n")
            if self.f_record:
                flo_record.write('\n')
                flo_record.write(title_name)
                flo_record.write('\n')
                flo_record.write('===========================================================\n')
                flo_record.write('\n')
                flo_record.write("delay time [" + str(delay_time) + "] current [" + str(self.leds._bcr) + "]\n")
                flo_record.write('\n')

            pro_bar = 0

            chan0 = AnalogIn(ads, ADS.P3)
            chanref = AnalogIn(ads, ADS.P2)
            chan1 = AnalogIn(ads, ADS.P1)

            chan_dark[0] = chan0.value
            ref_dark = chanref.value
            chan_dark[1] = chan1.value

            if self.Fluorometer_type == 'Blue':
                self.leds[1] = (65535, 65535, 65535)  # led Blue on
            elif self.Fluorometer_type == 'Red':
                self.leds[0] = (65535, 65535, 65535)  # led Red on
            else:
                print('Led error')
                return

            self.leds.show()
            time.sleep(delay_time)  # delay

            if self.f_record:
                flo_record.write("========  ========  ========  ========  ========  ========\n")
                flo_record.write("CH1 Dark  CH1       CH2 Dark  CH2       Ref Dark  Ref\n")
                flo_record.write("========  ========  ========  ========  ========  ========\n")
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
                print(
                    '{0:<7}  {1:<7}  {2:<7}  {3:<7}  {4:<7}  {5:<7}\n'.format(chan_dark[0], chan_light[0], chan_dark[1],
                                                                              chan_light[1], ref_dark, ref_light))
                # print(str(chan_dark[0]) + " " + str(chan_light[0]) + " " + \
                # str(chan_dark[1]) + " " + str(chan_light[1]) + " " + \
                # str(ref_dark) + " " + str(ref_light))

                if self.f_record:
                    # flo_record.write(str(chan_dark[0]) +" "+str(chan_light[0]) +" "+ \
                    # str(chan_dark[1]) +" "+str(chan_light[1]) +" "+ \
                    # str(ref_dark) + " " + str(ref_light) + "\n")
                    flo_record.write(
                        '{0:<8}  {1:<8}  {2:<8}  {3:<8}  {4:<8}  {5:<8}\n'.format(chan_dark[0], chan_light[0],
                                                                                  chan_dark[1], chan_light[1], ref_dark,
                                                                                  ref_light))

                pro_bar += 100 / s_times
                self.pop_up.set_bar(pro_bar)

            if self.Fluorometer_type == 'Blue':
                self.leds[1] = (0, 0, 0)  # led Blue off
            elif self.Fluorometer_type == 'Red':
                self.leds[0] = (0, 0, 0)  # led Red off
            else:
                print('Led error')
                return
            self.leds.show()

            if self.f_record:
                flo_record.write("========  ========  ========  ========  ========  ========\n")
                flo_record.write("\n")
            chan_result[0] = chan_sum[0] / s_times - chan_dark[0]
            chan_result[1] = chan_sum[1] / s_times - chan_dark[1]
            ref_result = ref_sum / s_times - ref_dark

            # show result
            chan_result[0] = round(chan_result[0], 1)
            chan_result[1] = round(chan_result[1], 1)
            ref_result = round(ref_result, 1)

            print("result led continue: ")
            print('Dark: ' + str(chan_dark[0]) + " " + str(chan_dark[1]) + " " + str(ref_dark))
            print(
                'Aver: ' + str(chan_sum[0] / s_times) + " " + str(chan_sum[1] / s_times) + " " + str(ref_sum / s_times))
            print('Sub: ' + str(chan_result[0]) + " " + str(chan_result[1]) + " " + str(ref_result))
            print('------------------------')

            self.flo_read[0] = str(chan_result[0])
            self.flo_read[1] = str(ref_result)
            self.flo_read[2] = str(chan_result[1])

            chan_gap[0] = chan0max - chan0min
            chan_gap[1] = chan1max - chan1min
            ref_gap = refmax - refmin

            print('Gap:')
            print('Max: ' + str(chan0max) + " " + str(chan1max) + " " + str(refmax))
            print('Min: ' + str(chan0min) + " " + str(chan1min) + " " + str(refmin))
            print('Result: ' + str(chan_gap[0]) + " " + str(chan_gap[1]) + " " + str(ref_gap))
            print('------------------------------------------------------------------------------')
            self.gap_read[0] = str(chan_gap[0])
            self.gap_read[1] = str(ref_gap)
            self.gap_read[2] = str(chan_gap[1])

            if self.f_record:
                flo_record.write("Result\n")
                flo_record.write("\n")
                flo_record.write("========  ========  ========  ========\n")
                flo_record.write("Result    CH1       CH2       Ref\n")
                flo_record.write("========  ========  ========  ========\n")
                flo_record.write('Dark      {0:<8}  {1:<8}  {2:<8}\n'.format(chan_dark[0], chan_dark[1], ref_dark))
                flo_record.write(
                    'Aver      {0:<8}  {1:<8}  {2:<8}\n'.format(chan_sum[0] / s_times, chan_sum[1] / s_times,
                                                                ref_sum / s_times))
                flo_record.write(
                    'Sub       {0:<8}  {1:<8}  {2:<8}\n'.format(chan_result[0], chan_result[1], ref_result))
                flo_record.write('Gap       {0:<8}  {1:<8}  {2:<8}\n'.format(chan_gap[0], chan_gap[1], ref_gap))
                flo_record.write("========  ========  ========  ========\n")
                flo_record.write("\n")
                # flo_record.write('Dark: ' + str(chan_dark[0]) + " " + str(chan_dark[1]) + " " + str(ref_dark) + "\n")
                # flo_record.write('Aver: ' + str(chan_sum[0]/s_times)+ " " +str(chan_sum[1]/s_times) + " " +str(ref_sum/s_times) + "\n")
                # flo_record.write('Sub: ' + str(chan_result[0])+ " " +str(chan_result[1]) + " " +str(ref_result) + "\n")
                # flo_record.write('---------------------------------------------------------------------------------------------------------------------------\n')
                flo_record.close()

            self.pop_up.dismiss()

        except:
            self.pop_up.dismiss()
            print('ADC average led no blink failed')

    def adc_aver_with_blink_sub_gaincontrol_thread(self):  # blink with sub test
        t = time.localtime()
        index_name = 'LED Blink ' + str(time.strftime("%H_%M_%S", t))
        record_name = self.path_dir + '/' + index_name

        self.f_record = False
        # flo_record = open(record_name, "w")

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

        # comment if auto-record
        # if self.f_record:
        # flo_record = open(self.name, "a")
        try:
            pro_bar = 0
            ads = ADS.ADS1115(self.i2c, gain=gain_input, data_rate=sample_rate_input, address=0x48)
            chan0 = AnalogIn(ads, ADS.P3)
            chanref = AnalogIn(ads, ADS.P2)
            chan1 = AnalogIn(ads, ADS.P1)

            title_name = 'Fluorometer'
            # --------------------------first read------------------
            for ap in gainrange:
                pass_flag = True
                print('')
                print('')
                print(title_name)
                print(
                    "-----------start over with amplify [" + str(ap) + "] gain [" + str(gain_input) + "]--------------")
                print("-----------delay time [" + str(delay_time) + "] current [" + str(
                    self.leds.bcr) + "] ------------\n")
                '''
                if self.f_record:
                    flo_record.write('\n')
                    flo_record.write(title_name)
                    flo_record.write('\n')
                    flo_record.write('===========================================================\n')
                    flo_record.write('\n')
                    flo_record.write("start over with amplify [" + str(ap) + "] gain [" + str(gain_input) + "]\n")
                    flo_record.write('\n')
                    flo_record.write('\n')
                    flo_record.write("delay time [" + str(delay_time) + "] current [" + str(self.leds._bcr) + "]\n")
                    flo_record.write('\n')
                '''
                chan_dark[0] = chan0.value
                ref_dark = chanref.value
                chan_dark[1] = chan1.value

                # led first on
                if self.Fluorometer_type == 'Blue':
                    self.leds[1] = (65535, 65535, 65535)  # led Blue on
                elif self.Fluorometer_type == 'Red':
                    self.leds[0] = (65535, 65535, 65535)  # led Red on
                else:
                    print('Led error')
                    return
                self.leds.show()

                time.sleep(delay_time)  # delay

                chan_light[0] = chan0.value
                ref_light = chanref.value
                chan_light[1] = chan1.value

                for read in chan_light:
                    if read > 25000:
                        print("-------reach max, reducing gain-------")
                        '''
                        if self.f_record:
                            flo_record.write('\n')
                            flo_record.write("reach max, reducing gain\n")
                            flo_record.write('\n')
                        '''
                        gain_input = gain_input / 2

                        if gain_input < 1:
                            print('reach minimal gain, abort')
                            '''
                            if self.f_record:
                                flo_record.write('\n')
                                flo_record.write('reach minimal gain, abort\n')
                                flo_record.write('\n')
                            '''
                            self.pop_up.dismiss()
                            return

                        # led reset off
                        if self.Fluorometer_type == 'Blue':
                            self.leds[1] = (0, 0, 0)  # led Blue off
                        elif self.Fluorometer_type == 'Red':
                            self.leds[0] = (0, 0, 0)  # led Red off
                        else:
                            print('Led off error')
                            return
                        self.leds.show()

                        time.sleep(delay_time)  # delay
                        ads = ADS.ADS1115(self.i2c, gain=gain_input, data_rate=sample_rate_input, address=0x48)
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

            # if chan0min > chan_sub[0]:
            chan0min = chan_sub[0]
            # if chan0max < chan_sub[0]:
            chan0max = chan_sub[0]

            # if chan1min > chan_sub[1]:
            chan1min = chan_sub[1]
            # if chan1max < chan_sub[1]:
            chan1max = chan_sub[1]

            # if refmin > ref_sub:
            refmin = ref_sub
            # if refmax < ref_sub:
            refmax = ref_sub

            chan_sum[0] = chan_sum[0] + chan_sub[0]
            chan_sum[1] = chan_sum[1] + chan_sub[1]
            ref_sum = ref_sum + ref_sub

            print(str(chan_dark[0]) + " " + str(chan_light[0]) + " " + str(chan_sub[0]) + "  " + \
                  str(chan_dark[1]) + " " + str(chan_light[1]) + " " + str(chan_sub[1]) + "  " + \
                  str(ref_dark) + " " + str(ref_light) + " " + str(ref_sub))
            '''
            if self.f_record:
                flo_record.write(
                    "========  ========  ========  ========  ========  ========  ========  ========  ========\n")
                flo_record.write(
                    "CH1 Dark  CH1 Lit   CH1 Sub   CH2 Dark  CH2 Lit   CH2 Sub   Ref Dark  Ref Lit   Ref Sub\n")
                flo_record.write(
                    "========  ========  ========  ========  ========  ========  ========  ========  ========\n")

                flo_record.write(
                    '{0:<8}  {1:<8}  {2:<8}  {3:<8}  {4:<8}  {5:<8}  {6:<8}  {7:<8}  {8:<8}\n'.format(chan_dark[0],
                                                                                                      chan_light[0],
                                                                                                      chan_sub[0],
                                                                                                      chan_dark[1],
                                                                                                      chan_light[1],
                                                                                                      chan_sub[1],
                                                                                                      ref_dark,
                                                                                                      ref_light,
                                                                                                      ref_sub))
            '''
            # flo_record.write(str(chan_dark[0]) +" "+str(chan_light[0]) +" "+ str(chan_sub[0]) + "  " + \
            # str(chan_dark[1]) +" "+str(chan_light[1]) +" "+ str(chan_sub[1]) + "  " + \
            # str(ref_dark) + " " + str(ref_light) + " " + str(ref_sub) + "\n")

            # led first off
            if self.Fluorometer_type == 'Blue':
                self.leds[1] = (0, 0, 0)  # led Blue off
            elif self.Fluorometer_type == 'Red':
                self.leds[0] = (0, 0, 0)  # led Red off
            else:
                print('Led off error')
                return
            self.leds.show()

            pro_bar += 100 / s_times
            self.pop_up.set_bar(pro_bar)
            time.sleep(delay_time)  # delay

            # -------------------------read else 9----------------------
            for i in range(s_times - 1):
                chan_dark[0] = chan0.value
                ref_dark = chanref.value
                chan_dark[1] = chan1.value

                # led loop on
                if self.Fluorometer_type == 'Blue':
                    self.leds[1] = (65535, 65535, 65535)  # led Blue on
                elif self.Fluorometer_type == 'Red':
                    self.leds[0] = (65535, 65535, 65535)  # led Red on
                else:
                    print('Led error')
                    return
                self.leds.show()

                time.sleep(delay_time)  # delay

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

                print(str(chan_dark[0]) + " " + str(chan_light[0]) + " " + str(chan_sub[0]) + "  " + \
                      str(chan_dark[1]) + " " + str(chan_light[1]) + " " + str(chan_sub[1]) + "  " + \
                      str(ref_dark) + " " + str(ref_light) + " " + str(ref_sub))
                '''
                if self.f_record:
                    # flo_record.write(str(chan_dark[0]) +" "+str(chan_light[0]) +" "+ str(chan_sub[0]) + "  " + \
                    # str(chan_dark[1]) +" "+str(chan_light[1]) +" "+ str(chan_sub[1]) + "  " + \
                    # str(ref_dark) + " " + str(ref_light) + " " + str(ref_sub) + "\n")
                    flo_record.write(
                        '{0:<8}  {1:<8}  {2:<8}  {3:<8}  {4:<8}  {5:<8}  {6:<8}  {7:<8}  {8:<8}\n'.format(chan_dark[0],
                                                                                                          chan_light[0],
                                                                                                          chan_sub[0],
                                                                                                          chan_dark[1],
                                                                                                          chan_light[1],
                                                                                                          chan_sub[1],
                                                                                                          ref_dark,
                                                                                                          ref_light,
                                                                                                          ref_sub))
                '''
                if self.Fluorometer_type == 'Blue':
                    self.leds[1] = (0, 0, 0)  # led Blue off
                elif self.Fluorometer_type == 'Red':
                    self.leds[0] = (0, 0, 0)  # led Red off
                else:
                    print('Led error')
                    return
                self.leds.show()  # led loop off

                time.sleep(delay_time)  # delay
                pro_bar += 100 / s_times
                self.pop_up.set_bar(pro_bar)
            '''
            if self.f_record:
                flo_record.write(
                    "========  ========  ========  ========  ========  ========  ========  ========  ========\n")
                flo_record.write("\n")
            '''
            chan_result[0] = chan_sum[0] / s_times
            chan_result[1] = chan_sum[1] / s_times
            ref_result = ref_sum / s_times

            chan_result[0] = round(chan_result[0], 1)
            chan_result[1] = round(chan_result[1], 1)
            ref_result = round(ref_result, 1)

            self.flo_read[0] = str(chan_result[0])
            self.flo_read[1] = str(ref_result)
            self.flo_read[2] = str(chan_result[1])

            chan_gap[0] = chan0max - chan0min
            ref_gap = refmax - refmin
            chan_gap[1] = chan1max - chan1min

            print("result blink sub with gain control: ")
            print(str(chan_result[0]) + " " + str(chan_result[1]) + " " + str(ref_result))
            print('Gap:')
            print('Max: ' + str(chan0max) + " " + str(chan1max) + " " + str(refmax))
            print('Min: ' + str(chan0min) + " " + str(chan1min) + " " + str(refmin))
            print('Result: ' + str(chan_gap[0]) + " " + str(chan_gap[1]) + " " + str(ref_gap))
            print('------------------------------------------------------------------------------')

            self.gap_read[0] = str(chan_gap[0])
            self.gap_read[1] = str(ref_gap)
            self.gap_read[2] = str(chan_gap[1])

            ads = ADS.ADS1115(self.i2c, gain=float(self.adc_gain), data_rate=sample_rate_input, address=0x48)

            store = JsonStore("{0}/{1}".format(self.path_dir, self.Fluorometer_type))  # json
            title_name_with_index = title_name + '#1'

            for index in range(1, 1000):
                if store.exists(title_name_with_index):
                    title_name_with_index = "{0}#{1}".format(title_name, index)
                else:
                    break

            if self.Fluorometer_type == 'Blue':
                store.put(title_name_with_index,
                          Assay_Name=self.Fluorometer_type,
                          Test_Date=str(time.strftime("%m/%d/%Y %H:%M_%S", t)),
                          Omec_tube_conc='',
                          Omec_tube_conc_units='',
                          Original_sample='',
                          Original_sample_units='',
                          Sample_Volume='',
                          Dilution_Factor='',
                          Std_1_RFU='',
                          Std_2_RFU='',
                          Std_3_RFU='',
                          Excitation=self.Fluorometer_type,
                          Emisson='Green',
                          Far_Red_RFU=self.flo_read[0],
                          Green_RFU=self.flo_read[2])  # json Blue

            elif self.Fluorometer_type == 'Red':
                store.put(title_name_with_index,
                          Assay_Name=self.Fluorometer_type,
                          Test_Date=str(time.strftime("%m/%d/%Y %H:%M_%S", t)),
                          Omec_tube_conc='',
                          Omec_tube_conc_units='',
                          Original_sample='',
                          Original_sample_units='',
                          Sample_Volume='',
                          Dilution_Factor='',
                          Std_1_RFU='',
                          Std_2_RFU='',
                          Std_3_RFU='',
                          Excitation=self.Fluorometer_type,
                          Emisson='Far Red',
                          Far_Red_RFU=self.flo_read[0],
                          Green_RFU='')  # json Red
            else:
                print('Json error due to LED type')
                return
            '''
            if self.f_record:
                flo_record.write("Result\n")
                flo_record.write("\n")
                flo_record.write("========  ========  ========  ========\n")
                flo_record.write("Result    CH1       CH2       Ref\n")
                flo_record.write("========  ========  ========  ========\n")
                flo_record.write(
                    'Aver       {0:<8}  {1:<8}  {2:<8}\n'.format(chan_result[0], chan_result[1], ref_result))
                flo_record.write('Gap       {0:<8}  {1:<8}  {2:<8}\n'.format(chan_gap[0], chan_gap[1], ref_gap))
                flo_record.write("========  ========  ========  ========\n")
                flo_record.write("\n")
                flo_record.close()

                # flo_record.write("result blink sub with gain control: \n")
                # flo_record.write(str(chan_result[0])+ " " +str(chan_result[1]) + " " + str(ref_result) + "\n")
                # flo_record.write('---------------------------------------------------------------------------------------------------------------------------\n')
            '''
            self.pop_up.dismiss()

        except:
            self.pop_up.dismiss()
            '''
            if self.f_record:
                flo_record.write('ADC average blink sub with gain control failed\n')
            '''
            print('ADC average blink sub with gain control failed')

    '''     
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
    '''

    def adc_aver(self):
        self.show_popup()
        mythread = threading.Thread(target=self.adc_aver_thread)
        mythread.start()

    def adc_aver_with_led(self):
        self.show_popup()
        mythread = threading.Thread(target=self.adc_aver_with_led_thread)
        mythread.start()

    def adc_aver_with_blink_sub_gaincontrol(self):
        self.show_popup()
        mythread = threading.Thread(target=self.adc_aver_with_blink_sub_gaincontrol_thread)
        mythread.start()

    '''    
    def read_led_current(self):
        self.show_popup()
        mythread = threading.Thread(target=self.read_led_current_thread)
        mythread.start()
            
    def create_fluorometer_record(self):
        t = time.localtime()
        self.name = time.strftime("%Y_%m_%d_%H_%M",t)
        self.record_name = self.name
        self.name = '/home/pi/Fluorometer/Records/' + self.name
        #self.name = '/home/pi/Fluorometer/Records/' + self.name + '.txt'
        self.f_record = True
        flo_record = open(self.name, "w")
    '''

    def export_to_usb(self):
        # try:
        global usb_path
        usb_path = usb_path[2:-2]

        f = open(usb_path)
        j_data = json.load(f)
        f.close()

        if os.path.exists('/home/pi/Fluorometer/Records/temp.csv'):
            os.remove('/home/pi/Fluorometer/Records/temp.csv')

        temp_csv = open('/home/pi/Fluorometer/Records/temp.csv', 'w+', encoding='utf-8')
        csv_writer = csv.writer(temp_csv)

        count = 0
        for test in j_data:
            if count == 0:
                header = j_data[test].keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(j_data[test].values())
        temp_csv.close()

        csv_name = 'OmecData_' + time.strftime('%Y' + '_' + '%m' + '_' + '%d' + '_' + '%H' + '%M' + '%S') + '.csv'
        print("file name is: " + csv_name)
        # os.rename('/home/pi/Fluorometer/Records/temp.csv', '/home/pi/Fluorometer/Records/' +csv_name)
        os.system("cp /home/pi/Fluorometer/Records/temp.csv /home/pi/Fluorometer/Records/{0}".format(csv_name))

        # csv_name = csv_name.replace(':','\:') #do before CP
        # command = "cp " + usb_path + " /mnt/"
        command = "cp /home/pi/Fluorometer/Records/{0} /mnt/".format(csv_name)
        print("copy command is: " + command)

        os.system("mount /dev/sda1 /mnt")
        os.system(command)  # os.system("cp -r home/pi/Fluorometer/Records/ /mnt/")
        time.sleep(3)
        os.system("sudo umount /mnt")
        os.remove('/home/pi/Fluorometer/Records/{0}'.format(csv_name))
        # except:
        #   print("export USB failed")

    # -----------------------------AccuClear DNA---------------------------------
    def read_AccuClear_standard_1_thread(self):
        print('read AccuClear stadndard 1')
        try:
            pro_bar = 0
            chan_dark = [0, 0]
            chan_light = [0, 0]
            chan_sub = [0, 0]
            chan_result = [0, 0]
            chan_sum = [0, 0]
            ref_sum = 0

            gainrange = [1, 2, 4, 8, 16]
            gain_input = 16
            delay_time = 0.05
            s_times = 5
            # --------------------------first read------------------
            ads = ADS.ADS1115(self.i2c, gain=gain_input, data_rate=16, address=0x48)
            chan0 = AnalogIn(ads, ADS.P3)
            chan1 = AnalogIn(ads, ADS.P1)
            for ap in gainrange:
                pass_flag = True
                print(
                    "-----------start over with amplify [" + str(ap) + "] gain [" + str(gain_input) + "]--------------")
                print("-----------delay time [" + str(delay_time) + "] current [" + str(
                    self.leds._bcr) + "] ------------\n")
                chan_dark[0] = chan0.value
                chan_dark[1] = chan1.value

                self.leds[1] = (65535, 65535, 65535)
                self.leds.show()  # led first on
                time.sleep(delay_time)  # delay

                chan_light[0] = chan0.value
                chan_light[1] = chan1.value

                if chan_light[1] > 30000:
                    print("-------reach max, reducing gain-------")
                    gain_input = gain_input / 2

                    if (gain_input < 1):
                        print('reach minimal gain, abort')
                        self.pop_up.dismiss()
                        # tbd:add screen show
                        return

                    self.leds[1] = (0, 0, 0)
                    self.leds.show()  # led reset off
                    time.sleep(delay_time)  # delay
                    ads = ADS.ADS1115(self.i2c, gain=gain_input, data_rate=16, address=0x48)
                    chan0 = AnalogIn(ads, ADS.P3)
                    chan1 = AnalogIn(ads, ADS.P1)
                    pass_flag = False

                if pass_flag:
                    break

            chan_sub[0] = (chan_light[0] - chan_dark[0]) * ap
            chan_sub[1] = (chan_light[1] - chan_dark[1]) * ap

            chan_sum[0] = chan_sum[0] + chan_sub[0]
            chan_sum[1] = chan_sum[1] + chan_sub[1]

            print(str(chan_dark[0]) + " " + str(chan_light[0]) + " " + str(chan_sub[0]) + "  " + \
                  str(chan_dark[1]) + " " + str(chan_light[1]) + " " + str(chan_sub[1]))

            self.leds[1] = (0, 0, 0)
            self.leds.show()  # led first off
            pro_bar += 100 / s_times
            self.pop_up.set_bar(pro_bar)
            time.sleep(delay_time)  # delay

            # -------------------------read else ----------------------
            for i in range(s_times - 1):
                chan_dark[0] = chan0.value
                chan_dark[1] = chan1.value

                self.leds[1] = (65535, 65535, 65535)
                self.leds.show()  # led loop on
                time.sleep(delay_time)  # delay

                chan_light[0] = chan0.value
                chan_light[1] = chan1.value

                chan_sub[0] = (chan_light[0] - chan_dark[0]) * ap
                chan_sub[1] = (chan_light[1] - chan_dark[1]) * ap

                chan_sum[0] = chan_sum[0] + chan_sub[0]
                chan_sum[1] = chan_sum[1] + chan_sub[1]

                print(str(chan_dark[0]) + " " + str(chan_light[0]) + " " + str(chan_sub[0]) + "  " + \
                      str(chan_dark[1]) + " " + str(chan_light[1]) + " " + str(chan_sub[1]))

                self.leds[1] = (0, 0, 0)
                self.leds.show()  # led loop off
                time.sleep(delay_time)  # delay
                pro_bar += 100 / s_times
                self.pop_up.set_bar(pro_bar)

            chan_result[0] = chan_sum[0] / s_times
            chan_result[1] = chan_sum[1] / s_times

            print(chan_result[0])
            print(chan_result[1])

            self.DNA_standard_1 = str(chan_result[1])
            self.DNA_last_read_1 = str(chan_result[1])
            FluorometerApp.config['AccuClear']['g'] = str(chan_result[1])
            with open('/home/pi/Fluorometer/config.ini', 'w') as configfile:
                FluorometerApp.config.write(configfile)

            # self.root.ids.sm.get_screen('Standard Table').ids.plot_dna.add_plot(self.plot)
            self.pop_up.dismiss()

        except:
            self.pop_up.dismiss()
            print('Accuclear standard 1 read failed')
            #test plot only
            chan_result[1] = 50

        #x = [100, 200, 300, 400, 500]
        #y = [chan_result[1]]
        # this will plot the signal on graph
        global fig
        fig = plt.figure(facecolor='w')
        plt.clf()
        #plt.style.use('dark_background')
        plt.xlim([0, 600])
        plt.ylim([0, 32767])
        #plt.plot(x, y)
        plt.plot(0, chan_result[1], 'ro')
        # setting x label
        plt.xlabel('OMEC tube concentration(ng/mL)', fontsize=8)

        # setting y label
        plt.yticks([])
        plt.ylabel('Fluorescence(RFUs)', fontsize=8)

        ax = plt.axes()
        ax.set_facecolor("w")
        # adding plot to kivy boxlayout
        self.root.get_screen('mainscreen').ids.sm.get_screen('Standard 1').ids.table_dna.add_widget(
            FigureCanvasKivyAgg(fig))


    def read_AccuClear_standard_2_thread(self):
        print('read AccuClear stadndard 2')
        try:

            pro_bar = 0
            chan_dark = [0, 0]
            chan_light = [0, 0]
            chan_sub = [0, 0]
            chan_result = [0, 0]
            chan_sum = [0, 0]
            ref_sum = 0

            gainrange = [1, 2, 4, 8, 16]
            gain_input = 16
            delay_time = 0.05
            s_times = 5
            # --------------------------first read------------------

            ads = ADS.ADS1115(self.i2c, gain=gain_input, data_rate=16, address=0x48)
            chan0 = AnalogIn(ads, ADS.P3)
            chan1 = AnalogIn(ads, ADS.P1)
            for ap in gainrange:
                pass_flag = True
                print(
                    "-----------start over with amplify [" + str(ap) + "] gain [" + str(gain_input) + "]--------------")
                print("-----------delay time [" + str(delay_time) + "] current [" + str(
                    self.leds._bcr) + "] ------------\n")
                chan_dark[0] = chan0.value
                chan_dark[1] = chan1.value

                self.leds[1] = (65535, 65535, 65535)
                self.leds.show()  # led first on
                time.sleep(delay_time)  # delay

                chan_light[0] = chan0.value
                chan_light[1] = chan1.value

                if chan_light[1] > 30000:
                    print("-------reach max, reducing gain-------")
                    gain_input = gain_input / 2

                    if (gain_input < 1):
                        print('reach minimal gain, abort')
                        self.pop_up.dismiss()
                        # tbd:add screen show
                        return

                    self.leds[1] = (0, 0, 0)
                    self.leds.show()  # led reset off
                    time.sleep(delay_time)  # delay
                    ads = ADS.ADS1115(self.i2c, gain=gain_input, data_rate=16, address=0x48)
                    chan0 = AnalogIn(ads, ADS.P3)
                    chan1 = AnalogIn(ads, ADS.P1)
                    pass_flag = False

                if pass_flag:
                    break

            chan_sub[0] = (chan_light[0] - chan_dark[0]) * ap
            chan_sub[1] = (chan_light[1] - chan_dark[1]) * ap

            chan_sum[0] = chan_sum[0] + chan_sub[0]
            chan_sum[1] = chan_sum[1] + chan_sub[1]

            print(str(chan_dark[0]) + " " + str(chan_light[0]) + " " + str(chan_sub[0]) + "  " + \
                  str(chan_dark[1]) + " " + str(chan_light[1]) + " " + str(chan_sub[1]))

            self.leds[1] = (0, 0, 0)
            self.leds.show()  # led first off
            pro_bar += 100 / s_times
            self.pop_up.set_bar(pro_bar)
            time.sleep(delay_time)  # delay

            # -------------------------read else ----------------------

            for i in range(s_times - 1):
                chan_dark[0] = chan0.value
                chan_dark[1] = chan1.value

                self.leds[1] = (65535, 65535, 65535)
                self.leds.show()  # led loop on
                time.sleep(delay_time)  # delay

                chan_light[0] = chan0.value
                chan_light[1] = chan1.value

                chan_sub[0] = (chan_light[0] - chan_dark[0]) * ap
                chan_sub[1] = (chan_light[1] - chan_dark[1]) * ap

                chan_sum[0] = chan_sum[0] + chan_sub[0]
                chan_sum[1] = chan_sum[1] + chan_sub[1]

                print(str(chan_dark[0]) + " " + str(chan_light[0]) + " " + str(chan_sub[0]) + "  " + \
                      str(chan_dark[1]) + " " + str(chan_light[1]) + " " + str(chan_sub[1]))

                self.leds[1] = (0, 0, 0)
                self.leds.show()  # led loop off
                time.sleep(delay_time)  # delay
                pro_bar += 100 / s_times
                self.pop_up.set_bar(pro_bar)

            chan_result[0] = chan_sum[0] / s_times
            chan_result[1] = chan_sum[1] / s_times

            print(chan_result[0])
            print(chan_result[1])

            self.DNA_standard_2 = str(chan_result[1])
            self.DNA_last_read_2 = str(chan_result[1])
            FluorometerApp.config['AccuClear']['v'] = str(chan_result[1])
            with open('/home/pi/Fluorometer/config.ini', 'w') as configfile:
                FluorometerApp.config.write(configfile)
            self.pop_up.dismiss()

        except:
            self.pop_up.dismiss()
            print('standard 2 read failed')
            #test matplot only
            chan_result[1] = 20000


        # blank_read = float(FluorometerApp.config['AccuClear']['g'])
        # self.plot = PointPlot(color=[1, 1, 1, 1])
        # self.root.ids.sm.get_screen('Standard Table').ids.plot_dna.remove_plot(self.plot)
        # self.plot.points = [(x, ((fake_read - blank_read)/500*x+blank_read)) for x in range(0,500)]

        # self.root.ids.sm.get_screen('Standard Table').ids.plot_dna.add_plot(self.plot)
        # self.root.ids['plot_dna'].add_plot(self.plot)

        # x = [100, 200, 300, 400, 500]
        # y = [chan_result[1]]
        # this will plot the signal on graph
        global fig
        fig = plt.figure()
        plt.xlim([0, 600])
        plt.ylim([0, 32767])
        # plt.plot(x, y)




        #g = float(FluorometerApp.config['AccuClear']['g'])
        g = 50
        x_values = [0, 250]
        y_values = [g, chan_result[1]]

        plt.plot(0, g, 'ro')
        plt.plot(250, chan_result[1], 'ro')
        plt.plot(x_values, y_values)

        # setting x label
        plt.xlabel('OMEC tube concentration(ng/mL)', fontsize=8)

        # setting y label
        plt.yticks([])
        plt.ylabel('Fluorescence(RFUs)', fontsize=8)

        ax = plt.axes()
        ax.set_facecolor("w")
        # adding plot to kivy boxlayout
        self.root.get_screen('mainscreen').ids.sm.get_screen('Standard Table').ids.table_dna.add_widget(
            FigureCanvasKivyAgg(fig))

    def DNA_AccuClear_read_tube_thread(self):
        print('read AccuClear tube')
        try:
            t = time.localtime()
            index_name = 'AccuClear ' + str(time.strftime("%H:%M_%S", t))
            record_name = self.path_dir + '/' + index_name
            self.f_record = False
            # flo_record = open(record_name, "w")
            title_name = 'AccuClear'

            pro_bar = 0
            chan_dark = [0, 0]
            chan_light = [0, 0]
            chan_sub = [0, 0]
            chan_result = [0, 0]
            chan_sum = [0, 0]
            ref_sum = 0

            gainrange = [1, 2, 4, 8, 16]
            gain_input = 16
            delay_time = 0.05
            s_times = 5

            # --------------------------first read------------------
            ads = ADS.ADS1115(self.i2c, gain=gain_input, data_rate=16, address=0x48)
            chan0 = AnalogIn(ads, ADS.P3)
            chan1 = AnalogIn(ads, ADS.P1)
            for ap in gainrange:
                pass_flag = True
                print(
                    "-----------start over with amplify [" + str(ap) + "] gain [" + str(gain_input) + "]--------------")
                print("-----------delay time [" + str(delay_time) + "] current [" + str(
                    self.leds._bcr) + "] ------------\n")
                '''
                if self.f_record:
                    flo_record.write('\n')
                    flo_record.write('===========================================================\n')
                    flo_record.write(title_name)
                    flo_record.write('\n')
                    flo_record.write('===========================================================\n')
                    flo_record.write('\n')
                    flo_record.write(str(time.strftime("%m/%d/%Y %H:%M", t)))
                    flo_record.write('\n')
                '''
                chan_dark[0] = chan0.value
                chan_dark[1] = chan1.value

                self.leds[1] = (65535, 65535, 65535)
                self.leds.show()  # led first on
                time.sleep(delay_time)  # delay

                chan_light[0] = chan0.value
                chan_light[1] = chan1.value

                if chan_light[1] > 30000:
                    print("-------reach max, reducing gain-------")
                    gain_input = gain_input / 2

                    if (gain_input < 1):
                        print('reach minimal gain, abort')
                        self.pop_up.dismiss()
                        # tbd:add screen show
                        return

                    self.leds[1] = (0, 0, 0)
                    self.leds.show()  # led reset off
                    time.sleep(delay_time)  # delay
                    ads = ADS.ADS1115(self.i2c, gain=gain_input, data_rate=16, address=0x48)
                    chan0 = AnalogIn(ads, ADS.P3)
                    chan1 = AnalogIn(ads, ADS.P1)
                    pass_flag = False

                if pass_flag:
                    break

            chan_sub[0] = (chan_light[0] - chan_dark[0]) * ap
            chan_sub[1] = (chan_light[1] - chan_dark[1]) * ap

            chan_sum[0] = chan_sum[0] + chan_sub[0]
            chan_sum[1] = chan_sum[1] + chan_sub[1]

            print(str(chan_dark[0]) + " " + str(chan_light[0]) + " " + str(chan_sub[0]) + "  " + \
                  str(chan_dark[1]) + " " + str(chan_light[1]) + " " + str(chan_sub[1]))

            self.leds[1] = (0, 0, 0)
            self.leds.show()  # led first off
            pro_bar += 100 / s_times
            self.pop_up.set_bar(pro_bar)
            time.sleep(delay_time)  # delay

            # -------------------------read else ----------------------

            for i in range(s_times - 1):
                chan_dark[0] = chan0.value
                chan_dark[1] = chan1.value

                self.leds[1] = (65535, 65535, 65535)
                self.leds.show()  # led loop on
                time.sleep(delay_time)  # delay

                chan_light[0] = chan0.value
                chan_light[1] = chan1.value

                chan_sub[0] = (chan_light[0] - chan_dark[0]) * ap
                chan_sub[1] = (chan_light[1] - chan_dark[1]) * ap

                chan_sum[0] = chan_sum[0] + chan_sub[0]
                chan_sum[1] = chan_sum[1] + chan_sub[1]

                print(str(chan_dark[0]) + " " + str(chan_light[0]) + " " + str(chan_sub[0]) + "  " + \
                      str(chan_dark[1]) + " " + str(chan_light[1]) + " " + str(chan_sub[1]))

                self.leds[1] = (0, 0, 0)
                self.leds.show()  # led loop off
                time.sleep(delay_time)  # delay
                pro_bar += 100 / s_times
                self.pop_up.set_bar(pro_bar)

            chan_result[0] = chan_sum[0] / s_times
            chan_result[1] = chan_sum[1] / s_times

            # print(chan_result[0])
            # print("channel 1: " + str(chan_result[1]))

            tube_read = chan_result[1]
            print('tube: ' + str(tube_read))
        except:
            self.pop_up.dismiss()
            print('read AccuClear tube failed')

        k = float(FluorometerApp.config['AccuClear']['k'])
        g = float(FluorometerApp.config['AccuClear']['g'])  # blank RFU
        # r = float(ShowcaseApp.config['AccuClear']['r'])  #just calculate, no need record
        n = float(FluorometerApp.config['AccuClear']['n'])
        v = float(FluorometerApp.config['AccuClear']['v'])  # high_end RFU
        s = float(FluorometerApp.config['AccuClear']['s'])  # high_standard_concentration 500ng/ml?

        r = (v - g) * ((pow(s, n) + k) / pow(s, n))

        if tube_read - g <= 0:
            self.DNA_result = str(tube_read)
            self.DNA_result_real = 'Reading too low'
            '''
            if self.f_record:
                flo_record.write("\n")
                flo_record.write('-----------------------------------------------------------\n')
                flo_record.write("\n")
                flo_record.write("Emission                   {0:<8}\n".format(chan_result[1]))
                flo_record.write("\n")
                flo_record.write('-----------------------------------------------------------\n')
                flo_record.write("\n")
                flo_record.write("Concentration            " + self.DNA_result_real + "\n")
                flo_record.write("\n")
                flo_record.write('-----------------------------------------------------------\n')
                flo_record.write("\n")
                flo_record.write("Excitation            Blue\n")
                flo_record.write("\n")
                flo_record.write('-----------------------------------------------------------\n')
                flo_record.close()
                
            '''
            self.pop_up.dismiss()
            return

        temp = r - (tube_read - g)
        if (temp != 0):
            result = pow(k * (tube_read - g) / (r - (tube_read - g)), 1 / n)

        if isinstance(result, complex):
            self.DNA_result = 'Reading too low'
            self.DNA_result_real = str(tube_read)
            print('still complex number detected')
            self.pop_up.dismiss()
            return

        result_real = result / self.DNA_volume
        result = format(result, '.3f')

        print('result: ' + str(result))

        # self.DNA_result = '{:.2f}'.format(result)
        self.DNA_result = result
        self.DNA_result_real = '{:.3f}'.format(result_real) + ' ' + self.DNA_unit

        store = JsonStore(self.path_dir + '/' + 'AccuClear')  # json
        title_name_with_index = title_name + ' #1'
        for index in range(1, 1000):
            if store.exists(title_name_with_index):
                title_name_with_index = title_name + ' #' + str(index)
            else:
                break

        store.put(title_name_with_index,
                  Assay_Name='dsDNA Broad Range',
                  Test_Date=str(time.strftime("%m/%d/%Y %H:%M_%S", t)),
                  Omec_tube_conc='',
                  Omec_tube_conc_units=self.DNA_unit,
                  Original_sample='{:.2f}'.format(result_real),
                  Original_sample_units=self.DNA_unit,
                  Sample_Volume=self.DNA_volume,
                  Dilution_Factor=200 / self.DNA_volume,
                  Std_1_RFU=g,
                  Std_2_RFU=v,
                  Std_3_RFU='',
                  Excitation='Blue',
                  Emisson='Green',
                  Far_Red_RFU=chan_result[0],
                  Green_RFU=chan_result[1])  # json AccuClear
        print('json store success')
        '''
        if self.f_record:
            flo_record.write("\n")
            flo_record.write('-----------------------------------------------------------\n')
            flo_record.write("\n")
            flo_record.write("Emission                   {0:<8}\n".format(chan_result[1]))
            flo_record.write("\n")
            flo_record.write('-----------------------------------------------------------\n')
            flo_record.write("\n")
            flo_record.write("Concentration            " + self.DNA_result_real + "\n")
            flo_record.write("\n")
            flo_record.write('-----------------------------------------------------------\n')
            flo_record.write("\n")
            flo_record.write("Excitation            Blue\n")
            flo_record.write("\n")
            flo_record.write('-----------------------------------------------------------\n')
            flo_record.close()
        '''
        # self.root.ids.sm.get_screen('DNA Result').ids.DNA_result.text = str(result)
        self.pop_up.dismiss()

    def read_AccuClear_standard_1(self):
        self.show_popup()
        self.go_screen('Standard 1')
        mythread = threading.Thread(target=self.read_AccuClear_standard_1_thread)
        mythread.start()

    def read_AccuClear_standard_2(self):
        self.show_popup()
        self.go_screen('Standard Table')
        mythread = threading.Thread(target=self.read_AccuClear_standard_2_thread)
        mythread.start()

    def read_AccuClear_tube(self):
        self.show_popup()

        mythread = threading.Thread(target=self.DNA_AccuClear_read_tube_thread)
        mythread.start()
        self.go_screen('DNA Result')

    # -----------------------------AccuGreen DNA---------------------------------
    def read_AccuGreen_standard_1_thread(self):
        print('read AccuGreen stadndard 1')
        try:
            s_times = 5
            pro_bar = 0
            chan_dark = [0, 0]
            chan_light = [0, 0]
            chan_sub = [0, 0]
            chan_result = [0, 0]
            chan_sum = [0, 0]
            ref_sum = 0

            ads = ADS.ADS1115(self.i2c, gain=16, data_rate=16, address=0x48)
            chan0 = AnalogIn(ads, ADS.P3)
            chanref = AnalogIn(ads, ADS.P2)
            chan1 = AnalogIn(ads, ADS.P1)

            for i in range(s_times):
                chan_dark[0] = chan0.value
                ref_dark = chanref.value
                chan_dark[1] = chan1.value

                self.leds[1] = (65535, 65535, 65535)
                self.leds.show()  # led loop on
                time.sleep(0.05)  # delay

                chan_light[0] = chan0.value
                ref_light = chanref.value
                chan_light[1] = chan1.value

                chan_sub[0] = chan_light[0] - chan_dark[0]
                ref_sub = ref_light - ref_dark
                chan_sub[1] = chan_light[1] - chan_dark[1]

                chan_sum[0] = chan_sum[0] + chan_sub[0]
                ref_sum = ref_sum + ref_sub
                chan_sum[1] = chan_sum[1] + chan_sub[1]

                print(str(chan_dark[0]) + " " + str(chan_light[0]) + " " + str(chan_sub[0]) + "  " + \
                      str(chan_dark[1]) + " " + str(chan_light[1]) + " " + str(chan_sub[1]) + "  " + \
                      str(ref_dark) + " " + str(ref_light) + " " + str(ref_sub))

                self.leds[1] = (0, 0, 0)
                self.leds.show()  # led loop off
                time.sleep(0.05)  # delay
                pro_bar += 20
                self.pop_up.set_bar(pro_bar)

            chan_result[0] = chan_sum[0] / s_times
            chan_result[1] = chan_sum[1] / s_times
            ref_result = ref_sum / s_times

            print(chan_result[0])
            print(chan_result[1])


        except:
            self.pop_up.dismiss()
            print('AccuGreen standard 1 read failed')

        self.DNA_standard_1 = str(chan_result[1])
        self.DNA_last_read_1 = str(chan_result[1])
        FluorometerApp.config['AccuGreen']['g'] = str(chan_result[1])

        with open('/home/pi/Fluorometer/config.ini', 'w') as configfile:
            FluorometerApp.config.write(configfile)

        # self.root.ids.sm.get_screen('Standard Table').ids.plot_dna.add_plot(self.plot)
        self.pop_up.dismiss()

    def read_AccuGreen_standard_2_thread(self):
        print('read AccuGreen stadndard 2')
        try:
            s_times = 5
            pro_bar = 0
            chan_dark = [0, 0]
            chan_light = [0, 0]
            chan_sub = [0, 0]
            chan_result = [0, 0]
            chan_sum = [0, 0]
            ref_sum = 0

            ads = ADS.ADS1115(self.i2c, gain=16, data_rate=16, address=0x48)
            chan0 = AnalogIn(ads, ADS.P3)
            chanref = AnalogIn(ads, ADS.P2)
            chan1 = AnalogIn(ads, ADS.P1)

            for i in range(s_times):
                chan_dark[0] = chan0.value
                ref_dark = chanref.value
                chan_dark[1] = chan1.value

                self.leds[1] = (65535, 65535, 65535)
                self.leds.show()  # led loop on
                time.sleep(0.05)  # delay

                chan_light[0] = chan0.value
                ref_light = chanref.value
                chan_light[1] = chan1.value

                chan_sub[0] = chan_light[0] - chan_dark[0]
                ref_sub = ref_light - ref_dark
                chan_sub[1] = chan_light[1] - chan_dark[1]

                chan_sum[0] = chan_sum[0] + chan_sub[0]
                ref_sum = ref_sum + ref_sub
                chan_sum[1] = chan_sum[1] + chan_sub[1]

                print(str(chan_dark[0]) + " " + str(chan_light[0]) + " " + str(chan_sub[0]) + "  " + \
                      str(chan_dark[1]) + " " + str(chan_light[1]) + " " + str(chan_sub[1]) + "  " + \
                      str(ref_dark) + " " + str(ref_light) + " " + str(ref_sub))

                self.leds[1] = (0, 0, 0)
                self.leds.show()  # led loop off
                time.sleep(0.05)  # delay
                pro_bar += 20
                self.pop_up.set_bar(pro_bar)

            chan_result[0] = chan_sum[0] / s_times
            chan_result[1] = chan_sum[1] / s_times
            ref_result = ref_sum / s_times

            print(chan_result[0])
            print(chan_result[1])


        except:
            self.pop_up.dismiss()
            print('AccuGreen standard 2 read failed')

        self.DNA_standard_2 = str(chan_result[1])
        self.DNA_last_read_2 = str(chan_result[1])
        FluorometerApp.config['AccuGreen']['v'] = str(chan_result[1])
        with open('/home/pi/Fluorometer/config.ini', 'w') as configfile:
            FluorometerApp.config.write(configfile)

        # blank_read = float(FluorometerApp.config['AccuClear']['g'])
        # self.plot = PointPlot(color=[1, 1, 1, 1])
        # self.root.ids.sm.get_screen('Standard Table').ids.plot_dna.remove_plot(self.plot)
        # self.plot.points = [(x, ((fake_read - blank_read)/500*x+blank_read)) for x in range(0,500)]

        # self.root.ids.sm.get_screen('Standard Table').ids.plot_dna.add_plot(self.plot)
        # self.root.ids['plot_dna'].add_plot(self.plot)
        self.pop_up.dismiss()

    def DNA_AccuGreen_read_tube_thread(self):
        print('read AccuGreen tube')
        # try:
        t = time.localtime()
        index_name = 'AccuGreen ' + str(time.strftime("%H:%M_%S", t))
        record_name = self.path_dir + '/' + index_name
        self.f_record = False
        # flo_record = open(record_name, "w")
        title_name = 'AccuGreen'

        s_times = 5
        pro_bar = 0
        chan_dark = [0, 0]
        chan_light = [0, 0]
        chan_sub = [0, 0]
        chan_result = [0, 0]
        chan_sum = [0, 0]
        ref_sum = 0

        ads = ADS.ADS1115(self.i2c, gain=16, data_rate=16, address=0x48)
        chan0 = AnalogIn(ads, ADS.P3)
        chanref = AnalogIn(ads, ADS.P2)
        chan1 = AnalogIn(ads, ADS.P1)
        '''
        if self.f_record:
            flo_record.write('\n')
            flo_record.write('===========================================================\n')
            flo_record.write(title_name)
            flo_record.write('\n')
            flo_record.write('===========================================================\n')
            flo_record.write('\n')
            flo_record.write(str(time.strftime("%m/%d/%Y %H:%M", t)))
            flo_record.write('\n')
        '''
        for i in range(s_times):
            chan_dark[0] = chan0.value
            ref_dark = chanref.value
            chan_dark[1] = chan1.value

            self.leds[1] = (65535, 65535, 65535)
            self.leds.show()  # led loop on
            time.sleep(0.05)  # delay

            chan_light[0] = chan0.value
            ref_light = chanref.value
            chan_light[1] = chan1.value

            chan_sub[0] = chan_light[0] - chan_dark[0]
            ref_sub = ref_light - ref_dark
            chan_sub[1] = chan_light[1] - chan_dark[1]

            chan_sum[0] = chan_sum[0] + chan_sub[0]
            ref_sum = ref_sum + ref_sub
            chan_sum[1] = chan_sum[1] + chan_sub[1]

            print(str(chan_dark[0]) + " " + str(chan_light[0]) + " " + str(chan_sub[0]) + "  " + \
                  str(chan_dark[1]) + " " + str(chan_light[1]) + " " + str(chan_sub[1]) + "  " + \
                  str(ref_dark) + " " + str(ref_light) + " " + str(ref_sub))

            self.leds[1] = (0, 0, 0)
            self.leds.show()  # led loop off
            time.sleep(0.05)  # delay
            pro_bar += 20
            self.pop_up.set_bar(pro_bar)

        chan_result[0] = chan_sum[0] / s_times
        chan_result[1] = chan_sum[1] / s_times

        # print(chan_result[0])
        # print("channel 1: " + str(chan_result[1]))

        tube_read = chan_result[1]
        print('tube: ' + str(tube_read))
        # except:
        # self.pop_up.dismiss()
        # print('read AccuGreen tube failed')

        k = float(FluorometerApp.config['AccuGreen']['k'])
        g = float(FluorometerApp.config['AccuGreen']['g'])  # blank RFU
        # r = float(ShowcaseApp.config['AccuGreen']['r'])  #just calculate, no need record
        n = float(FluorometerApp.config['AccuGreen']['n'])
        v = float(FluorometerApp.config['AccuGreen']['v'])  # high_end RFU
        s = float(FluorometerApp.config['AccuGreen']['s'])  # high_standard_concentration 500ng/ml?

        r = (v - g) * ((pow(s, n) + k) / pow(s, n))
        if tube_read - g <= 0:
            print('reading too low')
            self.DNA_result = str(tube_read)
            self.DNA_result_real = 'Reading too low'
            '''
            if self.f_record:
                flo_record.write("\n")
                flo_record.write('-----------------------------------------------------------\n')
                flo_record.write("\n")
                flo_record.write("Emission                   {0:<8}\n".format(chan_result[1]))
                flo_record.write("\n")
                flo_record.write('-----------------------------------------------------------\n')
                flo_record.write("\n")
                flo_record.write("Concentration            " + self.DNA_result_real + "\n")
                flo_record.write("\n")
                flo_record.write('-----------------------------------------------------------\n')
                flo_record.write("\n")
                flo_record.write("Excitation            Blue\n")
                flo_record.write("\n")
                flo_record.write('-----------------------------------------------------------\n')
                flo_record.close()
            '''
            self.pop_up.dismiss()
            return

        temp = r - (tube_read - g)
        if temp != 0:
            result = pow(k * (tube_read - g) / (r - (tube_read - g)), 1 / n)

        if isinstance(result, complex):
            self.DNA_result = 'Reading too low'
            self.DNA_result_real = str(tube_read)
            self.pop_up.dismiss()
            return

        result_real = result / self.DNA_volume
        result = format(result, '.3f')

        print('result: ' + str(result))

        # self.DNA_result = '{:.2f}'.format(result)
        self.DNA_result = result
        self.DNA_result_real = '{:.6f}'.format(result_real) + ' ' + self.DNA_unit
        print(self.DNA_result_real)

        store = JsonStore(self.path_dir + '/' + 'AccuGreen')  # json
        title_name_with_index = title_name + ' #1'
        for index in range(1, 1000):
            if store.exists(title_name_with_index):
                title_name_with_index = title_name + ' #' + str(index)
            else:
                break

        store.put(title_name_with_index,
                  Assay_Name='dsDNA Broad Range',
                  Test_Date=str(time.strftime("%m/%d/%Y %H:%M_%S", t)),
                  Omec_tube_conc='',
                  Omec_tube_conc_units=self.DNA_unit,
                  Original_sample='{:.2f}'.format(result_real),
                  Original_sample_units=self.DNA_unit,
                  Sample_Volume=self.DNA_volume,
                  Dilution_Factor=200 / self.DNA_volume,
                  Std_1_RFU=g,
                  Std_2_RFU=v,
                  Std_3_RFU='',
                  Excitation='Blue',
                  Emisson='Green',
                  Far_Red_RFU=chan_result[0],
                  Green_RFU=chan_result[1])  # json AccuGreen
        print('json store success')
        '''
        if self.f_record:
            flo_record.write("\n")
            flo_record.write('-----------------------------------------------------------\n')
            flo_record.write("\n")
            flo_record.write("Emission                   {0:<8}\n".format(chan_result[1]))
            flo_record.write("\n")
            flo_record.write('-----------------------------------------------------------\n')
            flo_record.write("\n")
            flo_record.write("Concentration            " + self.DNA_result_real + "\n")
            flo_record.write("\n")
            flo_record.write('-----------------------------------------------------------\n')
            flo_record.write("\n")
            flo_record.write("Excitation            Blue\n")
            flo_record.write("\n")
            flo_record.write('-----------------------------------------------------------\n')
            flo_record.close()
        '''
        self.pop_up.dismiss()

    def read_AccuGreen_standard_1(self):
        self.show_popup()
        self.go_screen('Standard 1')
        mythread = threading.Thread(target=self.read_AccuGreen_standard_1_thread)
        mythread.start()

    def read_AccuGreen_standard_2(self):
        self.show_popup()
        self.go_screen('Standard Table')
        mythread = threading.Thread(target=self.read_AccuGreen_standard_2_thread)
        mythread.start()

    def read_AccuGreen_tube(self):
        self.show_popup()

        mythread = threading.Thread(target=self.DNA_AccuGreen_read_tube_thread)
        mythread.start()
        self.go_screen('DNA Result')

    def load_table(self):

        x = [1, 2, 3, 4, 5]
        y = [5, 12, 6, 9, 15]
        # this will plot the signal on graph
        plt.style.use('dark_background')
        plt.plot(x, y)
        plt.plot(2, 12, 'ro')
        # setting x label
        plt.xlabel('OMEC tube concentration(ng/mL)')

        # setting y label
        plt.ylabel('Fluorescence(RFUs)')

        # adding plot to kivy boxlayout
        self.root.get_screen('mainscreen').ids.sm.get_screen('table').ids.matplot.add_widget(
            FigureCanvasKivyAgg(plt.gcf()))


if __name__ == '__main__':
    FluorometerApp().run()
