from machine import Pin
from utime import sleep
from lib.microdot import Microdot
import lib.mm_wlan as mm_wlan
from lib.uping import ping
import neopixel
import json
import asyncio

## Config ##

ssid = ''
password = ''
rackUnits = 12
ledPerUnit = 3
ledPin = Pin.board.GP0
refreshTime = 10

## Config ##

# Setup LED strip
leds = neopixel.NeoPixel(ledPin, ledPerUnit * rackUnits)

# Connect to WLAN
mm_wlan.connect_to_network(ssid, password)

# Set up socket and start listening
app = Microdot()

# Initialize server status
serverStatus = []

serverStatusFile = '/serverStatus.json'
# Check if serverStatus.json exists, if not create it
try:
    with open(serverStatusFile, 'r') as f:
        serverStatus = json.loads(f.read())
except OSError:
    with open(serverStatusFile, 'w') as f:
        f.write('[]')
    

# Fill out the serverStatus with default values
for i in range(rackUnits - len(serverStatus)):
    serverStatus.append({
        'type': 'none',
        'name': f'U{rackUnits-i}', # Cosmetic for web UI
        'target': '',
        'status': 'none'
    })

def saveStatus(): 
    with open(serverStatusFile, 'w') as f:
        f.write(json.dumps(serverStatus))

saveStatus()

@app.route('/')
def index(request):
    return 'TODO some config page'

@app.route('/status', methods=['GET', 'POST'])
def status(request):
    global serverStatus
    if request.method == 'POST':
        data = request.json
        if data:
            # TODO validate data
            serverStatus = data
            saveStatus()
    else:
        # Return current status
        return serverStatus


async def statusUpdate():
    while True:
        # 
        for i in range(rackUnits):
            currentStatus = serverStatus[i]
            if currentStatus['type'] == 'ping':
                pingData = ping(currentStatus['target'], quiet=True)

                if pingData[0] == pingData[1]:
                    currentStatus['status'] = 'green'
                elif pingData[1] > 0:
                    currentStatus['status'] = 'orange'
                else:
                    currentStatus['status'] = 'red'
            elif currentStatus['type'] == 'http':
                currentStatus['status'] = 'none' # TODO
            else:
                currentStatus['status'] = 'none'

            # Debug log
            print(f"{i}: {currentStatus['name']} ({currentStatus['target']}) - {currentStatus['type']} - {currentStatus['status']}")

        # Build LED string
        for i in range(rackUnits):
            currentStatus = serverStatus[i]
            if currentStatus['status'] == 'green':
                color = (0, 255, 0)
            elif currentStatus['status'] == 'orange':
                color = (255, 165, 0)
            elif currentStatus['status'] == 'red':
                color = (255, 0, 0)
            else:
                color = (0, 0, 0)
            
            for j in range(ledPerUnit):
                leds[i * ledPerUnit + j] = color
        leds.write()


        sleep(refreshTime)

app.run()

asyncio.run(statusUpdate())
