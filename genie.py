import RPi.GPIO as GPIO
import time

import argparse
parser = argparse.ArgumentParser(description='Control Energenie Switches')
parser.add_argument('onoff', choices = ['on', 'off'], help = "specify on or off")
parser.add_argument('socket', choices = [1, 2, 3, 4], type = int, help = "socket 1 .. 4")

class Genie(object):
    def __init__(self):
        # set the pins numbering mode
        GPIO.setmode(GPIO.BOARD)

        # Select the GPIO pins used for the encoder K0-K3 data inputs
        GPIO.setup(11, GPIO.OUT)
        GPIO.setup(15, GPIO.OUT)
        GPIO.setup(16, GPIO.OUT)
        GPIO.setup(13, GPIO.OUT)

        # Select the signal to select ASK/FSK
        GPIO.setup(18, GPIO.OUT)

        # Select the signal used to enable/disable the modulator
        GPIO.setup(22, GPIO.OUT)

        # Disable the modulator by setting CE pin lo
        GPIO.output (22, False)

        # Set the modulator to ASK for On Off Keying
        # by setting MODSEL pin lo
        GPIO.output (18, False)

        # Initialise K0-K3 inputs of the encoder to 0000
        GPIO.output (11, False)
        GPIO.output (15, False)
        GPIO.output (16, False)
        GPIO.output (13, False)

    def __del__(self):
        GPIO.cleanup()

    def on(self, socket):
        # Set K0-K3
        code = self.make_code('on', socket)
        print 'on code for socket %d is 0x%x' % (socket, code)
        self.set_code(code)

    def off(self, socket):
        # Set K0-K3
        code = self.make_code('off', socket)
        print 'off code for socket %d is 0x%x' % (socket, code)
        self.set_code(code)

    def set_code(self, code):
        for gpio in [11, 15, 16, 13]:
            value = code & 1
            GPIO.output (gpio, value)
            #print "set gpio %d to %d" % (gpio, value)
            code = code >> 1
        # let it settle, encoder requires this
        time.sleep(0.1)
        # Enable the modulator
        GPIO.output (22, True)
        # keep enabled for a period
        time.sleep(0.25)
        # Disable the modulator
        GPIO.output (22, False)

    def make_code(self, onoff, number):
        '''
            1111 and 0111 socket 1 ON and OFF
            1110 and 0110 socket 2 ON and OFF
            1101 and 0101 socket 3 ON and OFF
            1100 and 0100 socket 4 ON and OFF
        '''

        if onoff == 'on':
            onoff_flag = 1 << 3
        elif onoff == 'off':
            onoff_flag = 0
        else:
            RuntimeError('Invalid onoff parameter %r' % onoff)

        socket_map = [7, 6, 5, 4]
        socket_id = socket_map[number - 1]

        return onoff_flag | socket_id

def main():
    args = parser.parse_args()
    genie = Genie()
    if args.onoff == 'on':
        genie.on(args.socket)
    elif args.onoff == 'off':
        genie.off(args.socket)

def test():
    genie = Genie()
    for socket in [1, 2, 3, 4]:
        raw_input('hit return key to send socket %d ON code' % socket)
        genie.on(socket)

        raw_input('hit return key to send socket %d OFF code' % socket)
        genie.off(socket)

if __name__ == '__main__':
    main()

