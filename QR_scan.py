import sensor
import pyb
import ustruct
import time

LED = pyb.LED(1)

# Global Def
dataHead = 0x40
dataTail1 = 0x23
dataTail2 = 0x24
UART_rate = 9600

codePayload = []


# UART Init
uart = pyb.UART(3, UART_rate, timeout_char = 1000)

p1 = pyb.Pin("P6", pyb.Pin.OUT_PP)
p2 = pyb.Pin("P3", pyb.Pin.OUT_PP)
p2.off()

# sensor Init
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)          # (RGB565 or GRAYSCALE)
sensor.set_framesize(sensor.HVGA)               # SVGA(800x600) or QVGA (320x240)
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.skip_frames(time=3000)                   # Wait Sensor to stable

dataStr = ""
dataInt = None

while True:
    img = sensor.snapshot()                 # Take and return the image.

    for code in img.find_qrcodes():         # from picture get payload data, 0-24 commonly
        dataStr = code.payload()

        try:
            dataInt = int(dataStr)              # convert str 2 int
        except ValueError:
            pass

        if dataInt is not None:
            if dataInt not in codePayload:
                codePayload.append(dataInt)

                LED.on()
                p1.on()

                print("send:", dataHead, dataStr, dataTail1, dataTail2, sep=' ')
                uart.write(ustruct.pack(">BBBB", dataHead, dataInt, dataTail1, dataTail2))
                # uart.write(ustruct.pack(">BBBBB", dataHead, Xdata, Ydata, dataTail))
                # uart.write(ustruct.pack(">BBBBBBB", dataHead, 1data, ..., 4data, dataTail))

                time.sleep_ms(1000)

                print("get:", uart.read(), sep=' ')

                # exit channel
                # if uart.read(1) == 0xff:
                #    return

                LED.off()
                p1.off()

        dataStr = ""                        # clear
        dataInt = None

    time.sleep_ms(100)

