import struct
import time, threading
from MSP.serialGuard import SerialGuard
from MSP.value import TimedValue


class MSP:
    MSP_ATTITUDE = 108
    MSP_GPS = 106

    def __init__(self, port, baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.undigested = b""
        self.roll = TimedValue(0)
        self.pitch = TimedValue(0)
        self.yaw = TimedValue(0)

        self.lat = TimedValue(0)
        self.lon = TimedValue(0)
        self.gndSpd = TimedValue(0)
        self.alt = TimedValue(0)
        self.sats = TimedValue(0)
        self.fix = TimedValue(0)
        self.gndCrs = TimedValue(0)


        self.ser = SerialGuard(self.dataCallback, self.port, self.baudrate, True)
        self.t = threading.Thread(target=self.run, daemon=True)
        self.t.start()

    def run(self):
        while(1):
            time.sleep(0.2)
            self.request_attitude()
            self.request_gps()

    def tryReadingPacket(self, ss):
        #print("packet starts with", ss)
        if(len(ss) >= 4):
            pktDir = ss[2]
            pktLen = ss[3]
            if(len(ss) >= 4 + pktLen+2):
                #print(list(ss[:4+pktLen+1]), ss[:4+pktLen+2])
                return ss[:4+pktLen+2]
            else:
                return []
        else:
            return []

    def verifyPacket(self, packet):
        #print("packet is", packet)
        direction = packet[2]
        if(direction != ord(">")):
            return False
        
        chksum = packet[-1]
        cmd = packet[4]
        size = packet[3]
        calcSum = cmd ^ size
        payload = packet[5:5+size]
        for p in payload:
            calcSum = calcSum ^ p
        if(calcSum != chksum):
            return False
        
        return True



    def dataCallback(self, data):
        #print("data received", data, "\n", list(data))
        self.undigested += data
        #print(self.undigested)
        framesToParse = []
        starts = []
        for i, c in enumerate(self.undigested):
            if(c == ord("$")):
                starts.append(i)
        
        delPref = 0
        for i, s in enumerate(starts):
            p = self.tryReadingPacket(self.undigested[s:])
            if(len(p) != 0):
                correct = self.verifyPacket(p)
                if(correct):
                    id = p[4]
                    if(id == self.MSP_ATTITUDE):
                        self.handleMspAttitude(p)
                    elif(id == self.MSP_GPS):
                        self.handleMspGps(p)
                    else:
                        print("id is", id)

            delPref += len(p)
        
        self.undigested = self.undigested[delPref:]


    def handleMspGps(self, packet):
        data = packet[5:5+16]
        #lat, lon, gndSpd, alt, sats, fix = struct.unpack('<iihhBB', data)
        fix, sats, lat, lon, alt, gndSpd, gndCrs = struct.unpack("<BBiihhh", data)

        self.lat.value = lat / 1e7
        self.lon.value = lon / 1e7
        self.gndSpd.value = gndSpd / 100 # from cm/s to m/s
        self.alt.value = alt
        self.sats.value = sats
        self.fix.value = fix
        self.gndCrs.value = gndCrs/10


    def handleMspAttitude(self, packet):
        data = packet[5:5+6]
        self.roll.value, self.pitch.value, self.yaw.value = struct.unpack('<hhh', data[:6])
        self.roll.value /= 10.0 
        self.pitch.value /= 10.0
        self.yaw.value /= 1.0


    def _create_msp_packet(self, cmd, payload=b''):
        header = b'$M<'
        size = len(payload)
        checksum = size ^ cmd
        for b in payload:
            checksum ^= b
        return header + bytes([size, cmd]) + payload + bytes([checksum])



    def _send_msp(self, cmd, payload=b''):
        pkt = self._create_msp_packet(cmd, payload)
        self.ser.sendData(pkt, True)

    def request_gps(self):
        self.lat._state = TimedValue.REQUESTED
        self.lon._state = TimedValue.REQUESTED
        self.gndSpd._state = TimedValue.REQUESTED
        self.alt._state = TimedValue.REQUESTED
        self.sats._state = TimedValue.REQUESTED
        self.fix._state = TimedValue.REQUESTED

        self._send_msp(self.MSP_GPS)

    def request_attitude(self):
        self.roll._state = TimedValue.REQUESTED
        self.pitch._state = TimedValue.REQUESTED
        self.yaw._state = TimedValue.REQUESTED
        self._send_msp(self.MSP_ATTITUDE)



if __name__ == "__main__":
    fc = MSP(port="/dev/ttyACM0")  # or "COM3" on Windows

    # Get angles
    while(1):
        fc.request_attitude()
        fc.request_gps()

        time.sleep(0.01)
        print(fc.lat, fc.lon, fc.alt)
        print(fc.yaw, fc.pitch, fc.roll)

    fc.close()