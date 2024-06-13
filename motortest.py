import RPi.GPIO as GPIO

# Set pin numbering mode (choose one)
GPIO.setmode(GPIO.BCM)
# GPIO.setmode(GPIO.BOARD)

class MotorController:
    def __init__(self, in1, in2, en):
        print(self)
        self.in1 = in1
        self.in2 = in2
        self.en = en
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.en, GPIO.OUT)
        self.pwm = GPIO.PWM(self.en, 1000)
        self.pwm.start(25)
        
    def backward(self):
        print(self)
        GPIO.output(self.in1, GPIO.HIGH)
        GPIO.output(self.in2, GPIO.LOW)

    def forward(self):
        print(self)
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.HIGH)

    def stop(self):
        print(self)
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)

# Define GPIO pins for front left motor
fr_pins = {'in1': 24, 'in2': 23, 'en': 2}
fl_pins = {'in1': 22, 'in2': 27, 'en': 3}
br_pins = {'in1': 6, 'in2': 5, 'en': 14}
bl_pins = {'in1': 16, 'in2': 26, 'en': 15}

# Initialize motor controller for front left motor
fl = MotorController(**fl_pins)
print("2")
fr = MotorController(**fr_pins)
print("2")
bl = MotorController(**bl_pins)
print("2")
br = MotorController(**br_pins)

try:
    while True:
        direction = input("Enter direction (f for forward, b for backward, s for stop): ")
        if direction == 'f':
            fl.forward()
            fr.forward()
            br.forward()
            bl.forward()
        elif direction == 'b':
            fl.backward()
            fr.backward()
            br.backward()
            bl.backward()
        elif direction == "a":
            fl.backward()
            bl.forward()
            fr.forward()
            br.backward()
        elif direction == "d":
            fl.forward()
            bl.backward()
            fr.backward()
            br.forward()
        elif direction == 's':
            fl.stop()
            fr.stop()
            br.stop()
            bl.stop()
        else:
            print("Invalid input. Enter 'f' for forward, 'b' for backward, or 's' for stop.")

except KeyboardInterrupt:
    fl.stop()
    fr.stop()
    br.stop()
    bl.stop()
    GPIO.cleanup()
    print("\nProgram interrupted by user. GPIO Clean up done.")
