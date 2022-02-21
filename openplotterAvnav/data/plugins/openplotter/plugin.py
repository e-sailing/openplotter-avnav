import time

class Plugin:

	@classmethod
	def pluginInfo(cls):
		return {
		'description': 'openplotter plugin adjust avnav for easy use and transparent thema',
		}

	def __init__(self,api):
		"""
		initialize a plugins
		do any checks here and throw an exception on error
		do not yet start any threads!
		@param api: the api to communicate with avnav
		@type  api: AVNApi
		"""
		self.api = api # type: AVNApi
		#we register an handler for API requests
		#self.userAppId=self.api.registerUserApp(api.getBaseUrl()+"/plugin.html","openplotter-48.png")
		self.api.registerRestart(self.stop) #allow the user to disable the plugin

	def stop(self):
		pass

	def run(self):
		self.api.registerLayout("op", "openplotter.json")
		self.api.registerSettingsFile("op6","op_mobile.json")
		self.api.registerSettingsFile("op6T","op_mobile_transp.json")
		self.api.registerSettingsFile("op10T","op_tablet_transp.json")
		self.api.registerSettingsFile("op20T","op_pcmonitor_transp.json")

		self.api.log("started")
		self.api.setStatus('NMEA','running')
		while not self.api.shouldStopMainThread():
			time.sleep(1)

