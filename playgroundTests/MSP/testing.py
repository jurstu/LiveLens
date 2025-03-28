import serial
import struct
import time

class BetaflightMSPController:
    MSP_ATTITUDE = 108
    MSP_BATTERY_STATE = 130
    MSP_SET_RAW_RC = 200
    MSP_GET_RC = 105

    def __init__(self, port, baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    def connect(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        time.sleep(2)  # Let FC initialize
        print(f"Connected to {self.port} at {self.baudrate} baud")
        

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def _create_msp_packet(self, cmd, payload=b''):
        header = b'$M<'
        size = len(payload)
        checksum = size ^ cmd
        for b in payload:
            checksum ^= b
        return header + bytes([size, cmd]) + payload + bytes([checksum])

    def _send_msp(self, cmd, payload=b''):
        pkt = self._create_msp_packet(cmd, payload)
        self.ser.write(pkt)

    def _read_msp(self):
        start = time.time()
        while True:
            if self.ser.read(1) == b'$':
                if self.ser.read(1) == b'M':
                    direction = self.ser.read(1)
                    if direction != b'>':
                        continue
                    size = ord(self.ser.read(1))
                    cmd = ord(self.ser.read(1))
                    data = self.ser.read(size)
                    checksum = ord(self.ser.read(1))
                    return cmd, data
            if time.time() - start > self.timeout:
                return 0, []

    def get_attitude(self):
        self._send_msp(self.MSP_ATTITUDE)
        cmd, data = self._read_msp()
        if cmd == self.MSP_ATTITUDE:
            roll, pitch, yaw = struct.unpack('<hhh', data[:6])
            return roll / 10.0, pitch / 10.0, yaw / 10.0  # Degrees
        return None
    
    def get_rc(self):
        MSP_RC = 105
        self._send_msp(MSP_RC)
        cmd, data = self._read_msp()
        if cmd != MSP_RC:
            return []
            raise RuntimeError(f"Unexpected response: got {cmd}, expected {MSP_RC}")
        if len(data) < 16:
            raise ValueError(f"Invalid RC data length: expected 16, got {len(data)}")
        
        rc_channels = list(struct.unpack('<8H', data[:16]))
        return rc_channels


    def get_battery_voltage(self):
        self._send_msp(self.MSP_BATTERY_STATE)
        cmd, data = self._read_msp()
        if cmd == self.MSP_BATTERY_STATE:
            voltage = data[0]  # 0.1V units
            return voltage / 10.0
        return None

    def set_rc_values(self, rc_channels):
#        if len(rc_channels) != 8:
#            raise ValueError("RC channel list must contain exactly 8 values")
        payload = b''.join(struct.pack('<H', ch) for ch in rc_channels)
        self._send_msp(self.MSP_SET_RAW_RC, payload)




if __name__ == "__main__":
    fc = BetaflightMSPController(port="/dev/ttyUSB0")
    fc.connect()

    # Get angles
    while(1):
        ret = fc.get_attitude()
        if ret != None:
            roll, pitch, yaw = ret
            print(f"Attitude -> Roll: {roll}°, Pitch: {pitch}°, Yaw: {yaw}°")

        
        #     T     R     P     Y             
        rc = [1123, 1124, 1125, 1126] #, 1001, 1002, 1003, 1004]
        #rc = [1000, 1500, 1500, 1500, 1000, 1000, 1000, 1000]
        fc.set_rc_values(rc)
        print("RC values sent")
        print(fc.get_rc())

        




    # Get battery voltage
    voltage = fc.get_battery_voltage()
    print(f"Battery Voltage: {voltage:.1f} V")

    # Send sticks (e.g. throttle low, others centered)
    rc = [1000, 1500, 1500, 1500, 1000, 1000, 1000, 1000]
    fc.set_rc_values(rc)
    print("RC values sent")

    fc.close()
