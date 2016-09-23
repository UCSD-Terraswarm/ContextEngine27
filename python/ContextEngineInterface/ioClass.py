import gdp
import json
#import Adafruit_BluefruitLE
# Input/output class. Identifies the gcl_name and parameter_name for each input or output.

def collectTrace(gclHandle, param, start, stop):
    # this is the actual subscribe call
    gclHandle.multiread(start, stop-start+1)

    # timeout
    t = {'tv_sec':0, 'tv_nsec':500*(10**6), 'tv_accuracy':0.0}
    data = []
    while True:
        # This could return a None, after the specified timeout
        event = gdp.GDP_GCL.get_next_event(t)
        if event is None or event["type"] == gdp.GDP_EVENT_EOS:
            break
        datum = event["datum"]
        handle = event["gcl_handle"]
        data.append(float(json.loads(datum['data'])[param]))
    return data

class ioClass(object):
    # TODO: Fix number of passed parameters
    def __init__(self, d): 
                
        #if nameStr == "":
        #    raise ValueError ("Name must be provided.")
        #if paramName == "":
        #    raise ValueError ("JSON parameter name must be provided.") 
        #if srcSink == "":
        #    raise ValueError ("Source/Sink must be provided.")
        
        self.IO = d['dir']
        if d['dir'] == 'in':
            if d['source']  == "GDP_I":
                self.IOtype = 'GDP'
                # Assume that GCL already exists and create the GCL handle
                # Log name in GDP
                self.gclName = gdp.GDP_NAME(d['name'])
                self.gclHandle = gdp.GDP_GCL(self.gclName, gdp.GDP_MODE_RO)
            elif d['source'] == "BLE_I":
                print "BLE input init."
                self.IOtype = 'BLE'
                self.UART_service_UUID = d['service_uuid']
                self.tx_char_UUID = d['tx_char_uuid']
                self.rx_char_UUID = d['rx_char_uuid']
                self.ble = Adafruit_BluefruitLE.get_provider()
                self.ble.initialize()
                self.buff = ''
            else:
                raise ValueError("Undefined source for input: "+d['source'])
        if d['dir'] == 'out':
            if d['sink']  == "GDP_O":
                print d['name']
                self.IOtype = 'GDP'  
                # Log name in GDP
                self.gclName = gdp.GDP_NAME(d['name'])
                self.gclHandle = gdp.GDP_GCL(self.gclName, gdp.GDP_MODE_RO)
                key = d['key']
                password = d['password']
                if key == "" or password == "":
                    raise ValueError ("Key path and password must be provided.")
                else:
                    skey = gdp.EP_CRYPTO_KEY(filename=key,
                                keyform=gdp.EP_CRYPTO_KEYFORM_PEM,
                                flags=gdp.EP_CRYPTO_F_SECRET)
                    open_info = {'skey': skey}
                    
                    # TODO Bypass password prompt
                    # Assume that GCL already exists and create the GCL handle
                    self.gclHandle = gdp.GDP_GCL(self.gclName, gdp.GDP_MODE_RA, open_info)
        # JSON parameter name to be used in each log record
        self.param = d['param']
        # Lag from the current record. Can be used to implement time series functions.
        self.lag = d['lag']

        # Normalization method for data:
        # 'none': no normalization
        # 'lin': linear normalization: mean-zeroed and divided by std
        self.norm = d['norm']
        # Normalization parameters (i.e., avg, std etc.)
        self.normParam = {} 
        print 20
    
    
    print 66
    
    def processBLE(self, data):
        if data.find('{\"msg\"') != -1:
            print self.buff
            self.buff = ''
        self.buff = self.buff + str(data)
    print 5 
    def printTester(self):
        print self.gcl, self.param, self.lag
    def readLog(self, start, stop): 
        param = self.param
        handle = self.gclHandle            
        lag = self.lag
        trace = collectTrace(handle, param, start - lag, stop - lag)
        return trace
    def subscribe(self):
        if self.IO == 'in':
            if self.IOtype == 'BT':
                self.btSock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self.btSock.connect((self.btAddr, 1)) # Fixed to port 1
            elif self.IOtype == 'BLE':
                pass 
                """
                # Clear any cached data because both bluez and CoreBluetooth have issues with
                # caching data and it going stale.
                self.ble.clear_cached_data()
                # Get the first available BLE network adapter and make sure it's powered on.
                self.adapter = self.ble.get_default_adapter()
                self.adapter.power_on()
                print('Using adapter: {0}'.format(self.adapter.name))
                # Disconnect any currently connected UART devices.  Good for cleaning up and
                # starting from a fresh state.
                print('Disconnecting any connected UART devices...')
                self.ble.disconnect_devices([self.UART_service_UUID])
                # Scan for UART devices.
                print('Searching for UART device...') 
                try:
                    print 'bob'
                    self.adapter.start_scan(timeout_sec = 15)
                    # Search for the first UART device found (will time out after 60 seconds
                    # but you can specify an optional timeout_sec parameter to change it).
                    print 'bob'
                    self.device = self.ble.find_device(service_uuids=[self.UART_service_UUID])
                    if self.device is None:
                        raise RuntimeError('Failed to find UART device!')
                finally:
                    # Make sure scanning is stopped before exiting.
                    self.adapter.stop_scan()
                print('Connecting to device...')
                self.device.connect()   # Will time out after 60 seconds, specify timeout_sec parameter
                                        # to change the timeout.
                # Once connected do everything else in a try/finally to make sure the device
                # is disconnected when done.
                try:
                    # Wait for service discovery to complete for at least the specified
                    # service and characteristic UUID lists.  Will time out after 60 seconds
                    # (specify timeout_sec parameter to override).
                    print('Discovering services...')
                    self.device.discover([self.UART_service_UUID], [self.tx_char_UUID, self.rx_char_UUID])
                    # Find the UART service and its characteristics.
                    self.uart = self.device.find_service(self.UART_service_UUID)
                    self.rx = self.uart.find_characteristic(self.rx_char_UUID)
                    #tx = uart.find_characteristic(TX_CHAR_UUID)
                    # Write a string to the TX characteristic.
                    #print('Sending message to device...')
                    #tx.write_value('Hello world!\r\n')
                    # Turn on notification of RX characteristics using the callback above.
                    print('Subscribing to RX characteristic changes...')
                    self.rx.start_notify(processBLE)
                    # Now just wait for 30 seconds to receive data.
                    print('Waiting 35 seconds to receive data from the device...')
                    time.sleep(35)
                finally:
                    # Make sure device is disconnected on exit.
                    self.device.disconnect()
                """
            else:   # Assume GDP log
                self.gclHandle.subscribe(0, 0, None)
        else:
            raise ValueError ('Subscription is not defined for output ports')
    def getNextData(self):
        ## NOTE How to identify log?! next line. How to muliti-Log?!
        ## NOTE Maybe you subs to all and it returns event for each?!
            ## NOTE ^^ Yeah, exactly that.^^
        newRecord = gdp.GDP_GCL.get_next_event(None)
        newDataPoint = json.loads(newRecord['datum']['data'])['temperature_celcius']
#        print newDataPoint
        return newDataPoint
    def write(self, data):
        if self.IO == 'in':
            raise ValueError ('Cannot write to input port.')
        else:
            datDict = {"data": data}
            self.gclHandle.append(datDict)


