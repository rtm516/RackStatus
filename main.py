from machine import Pin
from lib.phew import server, connect_to_wifi, logging
from lib.uping import ping
import neopixel
import json
import uasyncio
import config

# Enable debug logging
logging.enable_logging_types(logging.LOG_DEBUG)

# Setup LED strip
leds = neopixel.NeoPixel(config.ledPin, config.ledPerUnit * config.rackUnits)

# Connect to WLAN
logging.info(f"> connecting to wifi network '{config.ssid}'")
ipAddr = connect_to_wifi(config.ssid, config.password, 10)
if ipAddr:
    logging.info(f"  - ip address: {ipAddr}")
else:
    logging.error('  - failed to connect to wifi')

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
for i in range(config.rackUnits - len(serverStatus)):
    serverStatus.append({
        'type': 'none',
        'name': f'U{config.rackUnits-i}', # Cosmetic for web UI
        'target': '',
        'status': 'none'
    })

def saveStatus(): 
    with open(serverStatusFile, 'w') as f:
        f.write(json.dumps(serverStatus))

saveStatus()

@server.route('/')
def index(request):
    return 'TODO some config page'

@server.route('/status', methods=['GET', 'POST'])
def status(request):
    global serverStatus
    if request.method == 'POST':
        data = request.data
        if data:
            # TODO validate data
            serverStatus = data
            saveStatus()
            return json.dumps({'status': 'ok'}), 200, {'Content-Type': 'application/json'}
        else:
            return json.dumps({'status': 'error', 'message': 'No data provided'}), 400, {'Content-Type': 'application/json'}
    else:
        # Return current status
        return json.dumps(serverStatus), 200, {'Content-Type': 'application/json'}

@server.catchall()
def my_catchall(request):
    return "No matching route", 404

async def statusUpdate():
    while True:
        logging.debug("> status update")
        for i in range(config.rackUnits):
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
            logging.debug(f"  - {i}: {currentStatus['name']} ({currentStatus['target']}) - {currentStatus['type']} - {currentStatus['status']}")

        # Build LED string
        for i in range(config.rackUnits):
            currentStatus = serverStatus[i]
            if currentStatus['status'] == 'green':
                color = (0, 255, 0)
            elif currentStatus['status'] == 'orange':
                color = (255, 165, 0)
            elif currentStatus['status'] == 'red':
                color = (255, 0, 0)
            else:
                color = (0, 0, 0)
            
            for j in range(config.ledPerUnit):
                leds[i * config.ledPerUnit + j] = color
        leds.write()


        await uasyncio.sleep(config.refreshTime)

# Setup status update task and start server
uasyncio.get_event_loop().create_task(statusUpdate())
server.run()
