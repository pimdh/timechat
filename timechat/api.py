from oauth2client.client import GoogleCredentials
from googleapiclient.errors import HttpError
from googleapiclient import discovery
import httplib2, urllib, urllib2
import json
import calendar
import pytz
from datetime import datetime
import os

class Api():
    DISCOVERY_URL = ('https://{api}.googleapis.com/'
                     '$discovery/rest?version={apiVersion}')
    def __init__(self):
        self.credentials = GoogleCredentials.get_application_default().\
                           create_scoped(
                               ['https://www.googleapis.com/auth/cloud-platform'])
        self.http=httplib2.Http()
        self.credentials.authorize(self.http)

        self.maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', None)
        if not self.maps_api_key:
            raise Exception("GOOGLE_MAPS_API_KEY env var not provided")
        
    def call(self, method, request):
        service = discovery.build('language', 'v1beta1',
                                  http=self.http, discoveryServiceUrl=self.DISCOVERY_URL)
        if method == 'entities':
            service_request = service.documents().analyzeEntities(body=request)
        elif method == 'syntax':
            service_request = service.documents().annotateText(body=request)
        else:
            raise NotImplementedError()
        return service_request.execute()

    def call_entities(self, sentence):
        request = {
            "document":{
                "type":"PLAIN_TEXT",
                "content":sentence
            },
            "encodingType":"UTF8"
        }
        try:
            return self.call('entities', request)
        except HttpError:
            return None

    def call_syntax(self, sentence):
        request = {
            "document":{
                "type":"PLAIN_TEXT",
                "content":sentence
            },
            "features":{
                "extractSyntax": True,
                "extractEntities": False,
                "extractDocumentSentiment": False,
            },
            "encodingType":"UTF8"
        }
        try:
            return self.call('syntax', request)
        except HttpError:
            return None

    def call_geocoding(self, location, lang):
        params = {
            'address': location,
            'key': self.maps_api_key,
            'language': lang
        }
        res = urllib2.urlopen("https://maps.googleapis.com/maps/api/geocode/json?"+
                              urllib.urlencode(params)).read()
        return json.loads(res)        

    def call_timezone(self, location):
        lat_lng = str(location['lat'])+','+str(location['lng'])

        timestamp_utc = calendar.timegm(datetime.utcnow().utctimetuple())
        params = {
            'location': lat_lng,
            'timestamp': timestamp_utc,
            'key': self.maps_api_key
        }
        res = urllib2.urlopen("https://maps.googleapis.com/maps/api/timezone/json?" +
                              urllib.urlencode(params)).read()
        return json.loads(res)

    def fetch_location_data(self, location, lang):
        location_data = self.call_geocoding(location, lang)

        if not location_data['results']:
            return None, None
        
        loc = location_data['results'][0]['geometry']['location']
        address = location_data['results'][0]['formatted_address']

        timezone_data = self.call_timezone(loc)

        timezone = timezone_data['timeZoneId']
        time = datetime.now(tz=pytz.timezone(timezone))

        return address, time
        
