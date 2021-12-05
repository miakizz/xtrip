import time
import board
import digitalio

print("hello blinky!")

FR = digitalio.DigitalInOut(board.D17)
FR.direction = digitalio.Direction.OUTPUT

RingMode = digitalio.DigitalInOut(board.D27)
RingMode.direction = digitalio.Direction.OUTPUT

Hook = digitalio.DigitalInOut(board.D22)
Hook.direction = digitalio.Direction.INPUT

while True:
    RingMode.value = True
    for i in range(0,25):
        FR.value = True
        time.sleep(1/50)
        FR.value = False
        time.sleep(1/50)
        if Hook.value == True:
            RingMode.value = False
            print('Off Hook')
            break
    else:
        RingMode.value = False
        time.sleep(3)
        continue
    break
