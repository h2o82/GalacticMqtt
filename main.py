#A Simple Galactic Unicorn Mqtt Scroller / Reader
#based on some code from https://github.com/ucl-casa-ce/Galactic-Unicorn-MQTT-Scroller
#used to subscribe and receive messages. I have tested this with Node-Red and it all seems great.
#It doesnt use async so its not as fancy, but it does what I need.
#Requires 2 files - main.py and the mqttlib.py.

# Do the imports
import time
import network
import machine
from machine import Pin
from mqttlib import MQTTClient
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY


# Ensure you fill in your wifi details below
wifi_ssid = "YOUR WIFI SSID"
wifi_password = "YOUR WIFI PASSWORD"

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
print("Connected to WiFi")

# Fill in your MQTT server and topic details here
mqtt_host = "HOSTNAME OR IP"
mqtt_username = ""  # Your mqtt username
mqtt_password = ""  # your mqtt password
mqtt_receive_topic = "MQTT TOPIC"  # The MQTT topic for your Adafruit IO Feed

# Enter the name of your client ID, can be anything you like
mqtt_client_id = "DISPLAY NAME"

# Initialize our MQTTClient and connect to the MQTT server
mqtt_client = MQTTClient(
        client_id=mqtt_client_id,
        server=mqtt_host,
        user=mqtt_username,
        password=mqtt_password)

# Setup the graphics 
# Below are constants for the colouring and speed.
PADDING = 2
MESSAGE_COLOUR = (255, 255, 255)
OUTLINE_COLOUR = (0, 0, 0)
MESSAGE = ""
#BACKGROUND_COLOUR = (10, 0, 96) # Blue
BACKGROUND_COLOUR = (255, 255, 0) # Yellow
HOLD_TIME = 2.0
STEP_TIME = 0.045 #Edit to slow down/speed up text - lower for faster scrolling

# Galactic Unicorn Objects
gu = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)
width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT

# Constants
STATE_PRE_SCROLL = 0
STATE_SCROLLING = 1
STATE_POST_SCROLL = 2
shift = 0
state = STATE_PRE_SCROLL

# set the font
graphics.set_font("bitmap8")

# calculate the message width so scrolling can happen
msg_width = graphics.measure_text(MESSAGE, 1)
last_time = time.ticks_ms()

retained = "0"

# subscribe and display below

def sub_cb(topic, msg, retained):
    print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
          
    # state constants
    brightness = 0.5
    gu.set_brightness(brightness)
    STATE_PRE_SCROLL = 0
    STATE_SCROLLING = 1
    STATE_POST_SCROLL = 2

    shift = 0
    state = STATE_PRE_SCROLL
    def outline_text(text, x, y):
        graphics.set_pen(graphics.create_pen(int(OUTLINE_COLOUR[0]), int(OUTLINE_COLOUR[1]), int(OUTLINE_COLOUR[2])))
        graphics.text(text, x - 1, y - 1, -1, 1)
        graphics.text(text, x, y - 1, -1, 1)
        graphics.text(text, x + 1, y - 1, -1, 1)
        graphics.text(text, x - 1, y, -1, 1)
        graphics.text(text, x + 1, y, -1, 1)
        graphics.text(text, x - 1, y + 1, -1, 1)
        graphics.text(text, x, y + 1, -1, 1)
        graphics.text(text, x + 1, y + 1, -1, 1)
        graphics.set_pen(graphics.create_pen(int(MESSAGE_COLOUR[0]), int(MESSAGE_COLOUR[1]), int(MESSAGE_COLOUR[2])))
        graphics.text(text, x, y, -1, 1)
    
    DATA = (msg.decode('utf-8'))
    MESSAGE = str("                " + DATA + "             ")
    
# calculate the message width so scrolling can happen
    msg_width = graphics.measure_text(MESSAGE, 1)

    last_time = time.ticks_ms()
       

    print (MESSAGE)
    
    # Set the buttons to actuall do something :-)
    while True:
        time_ms = time.ticks_ms()

        if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_UP):
            gu.adjust_brightness(+0.01)

        if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_DOWN):
            gu.adjust_brightness(-0.01)

        if state == STATE_PRE_SCROLL and time_ms - last_time > HOLD_TIME * 1000:
            if msg_width + PADDING * 2 >= width:
                state = STATE_SCROLLING
            last_time = time_ms

        if state == STATE_SCROLLING and time_ms - last_time > STEP_TIME * 1000:
            shift += 1
            if shift >= (msg_width + PADDING * 2) - width - 1:
                state = STATE_POST_SCROLL
                brightness = 0
                gu.set_brightness(brightness)
                gu.update(graphics)
                break
            last_time = time_ms
           

        if state == STATE_POST_SCROLL and time_ms - last_time > HOLD_TIME * 1000:
            state = STATE_PRE_SCROLL
            shift = 0
            last_time = time_ms
            

        graphics.set_pen(graphics.create_pen(int(BACKGROUND_COLOUR[0]), int(BACKGROUND_COLOUR[1]), int(BACKGROUND_COLOUR[2])))
        graphics.clear()

        outline_text(MESSAGE, x=PADDING - shift, y=2)

        # update the display
        gu.update(graphics)

        # pause for a moment
        time.sleep(0.001)

# So that we can respond to messages on an MQTT topic, we need a callback
# function that will handle the messages.
def mqtt_subscription_callback(topic, message):
    print (f'Topic {topic} received message {message}')  # Debug print out of what was received over MQTT
    sub_cb(topic, message, retained)

# Before connecting, tell the MQTT client to use the callback
mqtt_client.set_callback(mqtt_subscription_callback)
mqtt_client.connect()

# Once connected, subscribe to the MQTT topic
mqtt_client.subscribe(mqtt_receive_topic)
print("Connected and subscribed")

try:
    while True:
        # Infinitely wait for messages on the topic.
        # Note wait_msg() is a blocking call, if you're doing multiple things
        # on the Pico you may want to look at putting this on another thread.
        print(f'Waiting for messages on {mqtt_receive_topic}')
        mqtt_client.wait_msg()
except Exception as e:
    print(f'Failed to wait for MQTT messages: {e}')
finally:
    mqtt_client.disconnect()
    time.sleep(0.500)
    machine.reset()
