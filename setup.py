from lib.phew import server, access_point, dns, logging, render_template
from config import Config
import machine
import utime
import _thread

AP_NAME = 'RackStatus Setup'

# Load configuration
config = Config()

def machine_reset():
	utime.sleep(1)
	print("Rebooting...")
	machine.reset()

def startSetup():
	# Start the access point
	logging.info('> starting access point')

	ap = access_point(AP_NAME)
	ip = ap.ifconfig()[0]
	dns.run_catchall(ip)

	logging.info(f"> gathering ssids")
	ssids = []
	networks = ap.scan()
	for network in networks:
		ssid = network[0].decode('utf-8').strip()
		if ssid not in ssids and ssid != '':
			ssids.append(ssid)
	
	def index(request):
		return render_template('templates/setup.html', ssids=ssids)
	
	def bootstrapCss(request):
		return server.FileResponse('templates/bootstrap.min.css')
	
	def setup(request):
		# Get the form data
		ssid = request.form.get('ssidDrop')
		password = request.form.get('password')

		if ssid == '':
			ssid = request.form.get('ssidManual')
		
		if ssid and password:
			logging.info(f'> saving wifi credentials: {ssid}')
			config.ssid = ssid
			config.password = password
			_thread.start_new_thread(machine_reset, ())
			return render_template('templates/setup.html', ssids=ssids, message='Rebooting...')
		else:
			return render_template('templates/setup.html', ssids=ssids, message='Please fill in all fields.')
      
	def catchall(request):
		if request.headers.get("host") != ip:
			return render_template(f"templates/redirect.html", domain=ip)
		return "No matching route", 404

	server.add_route('/', index)
	server.add_route('/setup', setup, methods=['POST'])
	server.add_route('/bootstrap.min.css', bootstrapCss)
	server.set_callback(catchall)
	server.run()
