from .providerbase import ProviderBase
from ..dataobjects import Record

import sys
import os
import urllib
import urllib2
import xml.etree.cElementTree as et
import logging

class PDNSNetApi(ProviderBase):
    def __init__(self):
        ProviderBase.__init__(self)
        self.configvars['apikey']=None
        self.BASEURL="https://www.powerdns.net/services/express.asmx"
        self.zone_id_map={}
        self.logger=logging.getLogger('dnsbackup.dme')


    def lint(self):
        try:
            self.pepare()
        except Exception,e:
            print "pdnsnet API connect failed: %s"%(str(e))
            return False

        if len (self.zone_id_map)==0:
            print "No domains found - does your subscription include API access?"
            return False

        return True

    def get_zones(self):
        return sorted(self.zone_id_map.keys())

    def get_records(self,zonename):
        zonename = zonename.lower()
        zoneid = self.zone_id_map[zonename]
        apiresult = self.get_record_list(self.configvars['apikey'],zoneid)
        records=[]
        for rec in apiresult:
            #print et.tostring(rec)
            record = Record()
            #some records are broken in powerdnsnet's database :(
            if rec[2].text==None or rec[4].text==None:
                continue
            recname=rec[2].text.lower()
            if recname==zonename:
                recname=''
            else:
                recname=recname[0:-len(zonename)-1]
            record.name=recname
            record.zone=zonename

            record.type=rec[3].text.upper()
            record.ttl=rec[5].text
            record.content = rec[4].text
            if record.type in ['MX','SRV']:
                record.modifiers.append(rec[6].text)

            #fix bind style
            #append dots in soa
            if record.type=='SOA':
                content=record.content.split()
                content[0]=content[0]+'.'
                content[1]=content[1]+'.'
                content=" ".join(content)
                record.content = content

            if record.type in ['NS','MX','CNAME','PTR','SRV']:
                record.content+='.'

            records.append(record)
        return records


    def get_record_list(self, apikey,zoneid):
        url = self.BASEURL+'?apikey='+apikey

        headers = {
        'Content-Type': 'application/soap+xml; charset=utf-8'
        }
        data="""<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
          <soap12:Body>
            <listRecords xmlns="http://powerdns.net/express">
              <zoneId>%s</zoneId>
            </listRecords>
          </soap12:Body>
        </soap12:Envelope>"""%zoneid

        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req)
        the_page = response.read()
        tree=et.fromstring(the_page)
        body=tree[0]
        listRecordsResponse = body[0]
        listRecordsResult = listRecordsResponse[0]
        code = listRecordsResult[0]
        description = listRecordsResult[1]
        if code.text!='100':
            raise Exception("Failed to download record list for zone id=%s! Errcode=%s, Description=%s"%(zoneid,code.text,description.text))
            return None

        return listRecordsResult[2]



    def prepare(self):
        self.zone_id_map = self.get_zone_map()

    def get_zone_map(self):
        url = self.BASEURL+'?apikey='+self.configvars['apikey']

        headers = {
        'Content-Type': 'application/soap+xml; charset=utf-8'
        }

        data = """<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
          <soap12:Body>
            <listZones xmlns="http://powerdns.net/express" />
          </soap12:Body>
        </soap12:Envelope>"""
        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req)
        the_page = response.read()
        tree=et.fromstring(the_page)
        body=tree[0]
        listZonesResponse = body[0]
        listZonesResult = listZonesResponse[0]
        code = listZonesResult[0]
        description = listZonesResult[1]
        if code.text!='100':
            raise Exception("Failed to download zone list! Errcode=%s, Description=%s"%(code.text,description.text))

        zonelist = listZonesResult[2]

        zoneids={}

        for zone in zonelist:
            zoneid=None
            zonename=None
            for child in zone:
                if child.tag=='{http://powerdns.net/express}Id':
                    zoneid=child.text
                if child.tag=='{http://powerdns.net/express}Name':
                    zonename=child.text
            if zoneid!=None and zonename!=None:
                zoneids[zonename.lower()]=zoneid
            else:
                raise Exception("zone did not have name or id (name=%s, id=%s)"%(zonename,zoneid))
        return zoneids


    def cleanup(self):
        pass

