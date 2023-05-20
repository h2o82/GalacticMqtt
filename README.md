# GalacticMqtt
A Simple Galactic Unicorn Mqtt Scroller / Reader

So I was hunting round the internet for a simple MQTT message scroller for my Galactic Unicorn display.

The reason:
I use Node-Red to send a few MQTT messages across my network when certain devices want to alert other devices.
I didnt want a pre-baked home automation system as I am not too keen on already made solutions.

I took some code from https://github.com/ucl-casa-ce/Galactic-Unicorn-MQTT-Scroller but I could never get this working. It just seems to hang the pico.

Requirements:
Galactic Unicorn https://shop.pimoroni.com/products/galactic-unicorn?variant=40057440960595
(Might work with other displays but I havent worked that out)
Wifi
An MQTT server that it can read messages. (I use Node-Red)

Instructions:

Ensure your pico is running micropython.
You can get this here: https://github.com/pimoroni/pimoroni-pico/releases
Edit the main.py with your wifi details and MQTT details.
Send main.py and mqttlib.py to the pico on the GU. (remember to backup any main.py that you already have on there so you don't lose it!)

Enjoy!

Other information/instructions:

I have a CCTV camera hooked into motioneye which is running on a docker instance on a RPi4.
Motioneye sends a web GET request to my node red upon motion.

My Node Red flow is as follows:

HTTP In (GET, /ws)
          |
          |------------- Debug
          |
          |------------- Template (HTML) --------- HTTP Response
          |
          |------------- Change Node (Set Msg.Payload, Value "Motion detected")  ----------- MQTT Out Node (Server, Topic)   (Server is Localhost, Port 1883, MQTT V3.1.1)
          
When Node red receives a web GET request to http://server:1880/ws it sets the payload as "Motion Detected" and then publishes the message via MQTT out.

When the Web Get request is received the Template sets the content for the web request and then a web response sends it back out via the mqtt out. This means you can test the web page by navigating to the link mentioned above. I left the template default to state show the payload only.

I only have 1 device connected currently and I will be adding more as time goes on. Hopefully I wont find many bugs when adding more devices and more objects to the flow.




