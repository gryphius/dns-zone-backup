from .providerbase import ProviderBase
from ..dataobjects import Record

import dns
import dns.query
import dns.zone
import dns.rdatatype

import logging

class AXFR(ProviderBase):
    def __init__(self):
        ProviderBase.__init__(self)
        self.configvars['server']=None
        self.configvars['zones']=None
        self.logger=logging.getLogger('dnsbackup.axfr')


    def lint(self):
        return True

    def get_zones(self):
        return [x.strip() for x in self.configvars['zones'].split(',')]

    def get_records(self,zonename):
        zonename = zonename.lower()
        server = self.configvars['server']
        zone = dns.zone.from_xfr(dns.query.xfr(server, zonename, relativize=True,
lifetime=30.0), relativize=True)
        nodes = zone.nodes
        recordlist=[]
        for name,rrset in nodes.iteritems():
            for rec in rrset:
                #print dir(rec)
                for pack in rec:
                    r=Record()
                    r.zone=zonename
                    r.name=str(name)
                    #if rec.rdtype ==dns.rdatatype.MX:
                    #    r.modifiers.append(pack.preference)
                    #elif rec.rdtype == dns.rdatatype.SRV:
                    #    r.modifiers.append(pack.priority)
                    #    r.modifiers.append(pack.weight)
                    #print rec.rdata
                    #ugly hack: for now we use the str representation as content util we find out how to get the data for all packet types
                    r.content = str(pack)
                    r.ttl = rec.ttl
                    r.type = dns.rdatatype._by_value[rec.rdtype]
                    recordlist.append(r)
        return recordlist


    def prepare(self):
        pass

    def cleanup(self):
        pass

