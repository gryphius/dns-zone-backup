from providers import PROVIDERS

from ConfigParser import RawConfigParser
import logging
import traceback
from string import Template
import os

class DNSBackup(object):
    def __init__(self):
        self.config=RawConfigParser(
            {
                'enabled':'yes',
                'filetemplate':'zonebackup/${provider}/${zonename}.txt'
             }
        )
        self.logger=logging.getLogger('dnsbackup')

    def run(self,config=None):
        if config==None:
            config=self.config
        providers = self._create_providers(config)
        for provider in providers:
            self.logger.debug('Running provider %s'%provider.configsection)
            try:
                provider.prepare()
                zones = provider.get_zones()
                for zone in zones:
                    records = provider.get_records(zone)
                    filecontent = self.build_zone_file_content(zone,records)

                    vars=dict(zonename=zone,provider=provider.configsection)
                    filenametemplate=Template(config.get(provider.configsection,'filetemplate'))
                    filename=filenametemplate.safe_substitute(vars)
                    dirpath = os.path.dirname(filename)
                    self.logger.debug("Writing file %s"%filename)
                    if not os.path.isdir(dirpath):
                        os.makedirs(dirpath)
                    fp=open(filename,'w')
                    fp.write(filecontent)
                    fp.close()

            except:
                ex = traceback.format_exc()
                self.logger.error("Provider %s failed: %s"%(provider.configsection,ex))
                continue

    def _create_providers(self,config):
        allsections=config.sections()
        runsections=allsections[:]
        for sec in allsections:
            if not config.getboolean(sec,'enabled'):
                runsections.remove(sec)

        providers=[]
        for sec in runsections:
            providerinstance = self._init_provider(config,sec)
            providers.append(providerinstance)
        return providers

    def _init_provider(self,config,section):
        if not config.has_option(section,'provider'):
            self.logger.error('config section %s missing provider')
            return None
        provider=config.get(section,'provider').lower()
        if provider not in PROVIDERS:
            self.logger.error('config section %s unknown provider %s'%(section,provider))

        providerinstance = PROVIDERS[provider]()
        providerinstance.configsection=section
        for opt in config.options(section):
            if opt in ['provider','enabled']:
                continue
            providerinstance.configvars[opt]=config.get(section,opt)
        return providerinstance



    def build_zone_file_content(self, zonename ,recordlist):
        zonename=zonename.lower()
        origin=zonename+'.'
        buff="$ORIGIN %s\n"%origin
        for record in sorted(recordlist):
            buff+=(str(record))
            buff+="\n"
        return buff
