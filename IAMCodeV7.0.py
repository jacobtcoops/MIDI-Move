# Import everything from the microbit module
from microbit import *
from machine import time_pulse_us
import math

# Function for note on
def midiNoteOn(chan, n, vel):
    # Hexadecimal for note-on event (0x signifies we are using Hexadecimal)
    MIDI_NOTE_ON = 0x90

    # Exit the function if parameters are outside a specified range
    if chan > 15:
        return
    if n > 127:
        return
    if vel > 127:
        return

    # Variable to hold MIDI message - convert to a 'bytes' object
    msg = bytes([MIDI_NOTE_ON | chan, n, vel])
    # Send down the MIDI cable
    uart.write(msg)

# Function for note off
def midiNoteOff(chan, n, vel):
    # Hexadecimal for note-off event
    MIDI_NOTE_OFF = 0x80

    # Exit the function if parameters are outside a specified range
    if chan > 15:
        return
    if n > 127:
        return
    if vel > 127:
        return

    # Variable to hold MIDI message
    msg = bytes([MIDI_NOTE_OFF | chan, n, vel])

    # Send down the MIDI cable
    uart.write(msg)

# Function to set up a MIDI connection through the cable
def Start():
    # baudrate - The number of bits transmitted per second
    #   NOTE: MIDI is asynchronous, hence it has to be sent at a standard rate
    # bits - Number of bits of data being sent through MIDI
    # tx - Tge pin the data is being sent through
    uart.init(baudrate=31250, bits=8, parity=None, stop=1, tx=pin0)

# Function for control change
def midiControlChange(chan, n, value):
    # Hexadecimal for control change event (0x signifies we are using Hexadecimal)
    MIDI_CC = 0xB0

    # Exit the function if parameters are outside a specified range
    if chan > 15:
        return
    if n > 127:
        return
    if value > 127:
        return

    # Variable to hold MIDI message - convert to a 'bytes' object
    msg = bytes([MIDI_CC | chan, n, value])
    # Send down the MIDI cable
    uart.write(msg)

# MAIN PROGRAM

# Set up MIDI connection
Start()

# MIDI values for note b
BUTTON_B_NOTE = 63

# Intialise variables
on = False
lastA = False
lastB = False

# Ultrasonic sensor
trig = pin15
echo = pin14

# trigger pin set as an output, echo pin set as an input
trig.write_digital(0)
echo.read_digital()

# Heights
minHeight = 73
maxHeight = 127

# Constantly loop
while True:

    # Update a button status
    a = button_a.is_pressed()

    while a is True:
        a = button_a.is_pressed()
        lastA = True

    if lastA is True:
        if on is False:
            on = True
        elif on is True:
            on = False
    lastA = False

    # Update b button status
    b = button_b.is_pressed()

    # If button b is pressed, send the MIDI value for note b and trigger
    if b is True and lastB is False:
        midiNoteOn(0, BUTTON_B_NOTE, 127)
    # If button b is released, send the MIDI value for note b and stop trigger
    elif b is False and lastB is True:
        midiNoteOff(0, BUTTON_B_NOTE, 127)

    # Update last value to current value
    lastB = b

    if on is True:
        display.show(Image.YES)

        # Send pulse to the trigger pin on the sensor
        trig.write_digital(1)
        # TODO - WORK OUT IF SLEEP IS NEEDED HERE OR IF REMOVING PRINT STATEMENTS HAS
        # SOLVED ISSUES
        # sleep(10)
        trig.write_digital(0)
        # Time between pulse transmission on trig pin and pulse received on echo pin
        micros = time_pulse_us(echo, 1)
        # Convert from microseconds to seconds
        t_echo = micros/1000000
        # Calculate the distance of the object which reflected the ultrasonic signals
        dist_cm = int((t_echo / 2) * 34300)

        if dist_cm > maxHeight:
            sliderValue = 100
        elif dist_cm < minHeight:
            sliderValue = 0
        elif dist_cm < maxHeight and dist_cm > minHeight:
            scale = maxHeight - minHeight
            sliderValue = math.floor((dist_cm - minHeight) / scale * 127)
        midiControlChange(0, 24, sliderValue)
    elif on is False:
        display.show(Image.NO)

    # Wait for 100 ms
    sleep(100)

