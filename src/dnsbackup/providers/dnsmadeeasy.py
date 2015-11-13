from .providerbase import ProviderBase
from ..dataobjects import Record

import httplib2
import json
from time import strftime, gmtime
import hashlib
import hmac
import time


class DMEApi(ProviderBase):
    def __init__(self):
        ProviderBase.__init__(self)
        self.configvars['apikey']=None
        self.configvars['secret']=None
        self.api = None
        self.zone_id_map={}

    def lint(self):
        pass

    def get_zones(self):
        return sorted(self.zone_id_map.keys())

    def get_records(self,zonename):
        zonename=zonename.lower()
        apiresult = self.api.get_records_from_domain(self.zone_id_map[zonename])
        records=[]
        for rec in apiresult:
            record = Record()
            record.name=rec['name'].lower()
            record.zone=zonename

            record.type=rec['type']
            record.ttl=rec['ttl']
            record.content = rec['value']
            for value in ['mxLevel','priority','port']:
                if value in rec:
                    record.modifiers.append(rec[value])
            records.append(record)
        return records



    def prepare(self):
        self.api=DME2(self.configvars['apikey'],self.configvars['secret'])

        domains  = self.api.get_domains()
        if len(domains)>100:
            self.api.ratelimit=True
        for domaininfo in domains:
            zonename=domaininfo['name']
            zoneid=domaininfo['id']
            self.zone_id_map[zonename.lower()]=zoneid

    def cleanup(self):
        pass



class DME2(object):
    def __init__(self, apikey, secret):
        self.api = apikey
        self.secret = secret
        self.baseurl = 'http://api.dnsmadeeasy.com/V2.0/'
        self.lastconnect = 0 # to stay below the request limit, we make only one request every 2.1 secs
        self.ratelimit = False

    def _headers(self):
        currTime = self._get_date()
        hashstring = self._create_hash(currTime)
        headers = {'x-dnsme-apiKey': self.api,
                   'x-dnsme-hmac': hashstring,
                   'x-dnsme-requestDate': currTime,
                   'content-type': 'application/json'}
        return headers

    def _get_date(self):
        return strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())

    def _create_hash(self, rightnow):
        return hmac.new(self.secret.encode(), rightnow.encode(), hashlib.sha1).hexdigest()

    def _rest_connect(self, resource, method, data=''):
        while self.ratelimit and time.time()-self.lastconnect<2.1:
            time.sleep(0.1)
            continue
        self.lastconnect=time.time()
        http = httplib2.Http()
        response, content = http.request(self.baseurl + resource, method, body=data, headers=self._headers())
        if (response['status'] == "200" or  response['status'] == "201" ):
            if content:
                return json.loads(content.decode('utf-8'))
            else:
                return response
        else:
            raise Exception("Error talking to dnsmadeeasy: " + response['status'])


    def get_domains(self):
        """
        Returns list of all domains for your account
        """
        return self._rest_connect('dns/managed', 'GET')['data']


    ##########################################################################
    #  /dns/managed/{domainId} - operate on a single domain
    ##########################################################################

    def get_domain(self, domainId):
        """
        Returns the domain specified by its ID.
        """
        return self._rest_connect('dns/managed/' + str(domainId), 'GET')


    ##########################################################################
    #    /dns/managed/{domainId}/records - operate on multiple records for
    #       one domain
    ##########################################################################

    def get_records_from_domain(self, domainId):
        """
        Returns all records for the specified domain.
        """
        return self._rest_connect('dns/managed/' + str(domainId) + '/records','GET')['data']

