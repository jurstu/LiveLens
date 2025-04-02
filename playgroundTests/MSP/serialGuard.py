import time
from threading import Thread
import serial

tag = "serial"

class SerialGuard:
    def __init__(self, dataReceiveCallback, portName='/dev/ttyUSB0', portBaud=115200, raw=False):
        self.raw = raw
        self.portName = portName
        self.portBaud = portBaud
        self.receiveCallback = dataReceiveCallback
        self.end = False
        self.start()


    def start(self):
        self.thread = Thread(target=self.run, args=())
        self.thread.daemon = True  # Daemonize thread to kill upon main code escape
        self.thread.start()  # Start the execution

    def stop(self):
        self.end = True


    def run(self):

        while not self.end:
            try:
                self.serial = serial.Serial(self.portName, self.portBaud)
            except Exception as e:
                print(tag, "couldn't open serial: " + str(e))
                time.sleep(1)
                continue

            while not self.end:
                try:
                    data=self.serial.read(self.serial.in_waiting)
                except Exception as e:
                    print(tag, "error while reading data from serial" + str(e))
                    if(self.serial.is_open):
                        self.serial.close()
                        break
                if(self.raw == False):
                    try:
                        strdata = data.decode('utf-8')
                        self.receiveCallback(strdata)
                        time.sleep(0.01)
                    except Exception as e:
                        print(tag, "probably utf- conversion error: " + str(e))    
                        print(tag, "data was: " + str(data))    
                else:
                    self.receiveCallback(data)
                time.sleep(0.1)
            self.serial.close()
        
        self.serial.close()

    def sendData(self, data, raw=False):
        if (hasattr(self, 'serial')):
            if(self.serial.is_open):
                if(raw==False and self.raw == False):
                    self.serial.write((str(data)).encode('utf-8'))
                else:
                    self.serial.write(data)
            else:
                print(tag, "uart isn't open, not sending this data: " + str(data))
        else:
            print(tag, "uart isn't open, not sending this data: " + str(data))



    def isSerialOpen(self):
        if (hasattr(self, 'serial')):
            if(self.serial.is_open):
                return True
            else:
                return False
        else:
            return False


if __name__ == "__main__":

    def here(asdf):
        print(asdf)

    
    a = SerialGuard(here)
    
    

    while(1):
        time.sleep(1)
        a.sendData("qwer")
        