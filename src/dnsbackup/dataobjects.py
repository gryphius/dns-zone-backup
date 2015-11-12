
class Record(object):
    typesortorder = ['SOA', 'A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SRV']

    def __init__(self):
        self.zone=''
        self.name='' #hostname only without domain!
        self.type='A'
        self.ttl=3600
        self.content='' #provider is responsiple to set the trailing dot where applicable!
        self.modifiers=[] # record modifiers in correct order. MX: mx priority. SRV: priority,port

    def _typeorder(self,rtype): #order special types first
        if rtype in Record.typesortorder:
            return (Record.typesortorder.index(rtype)+1)*'.'
        else:
            return rtype

    def __lt__(self,other):
        if not isinstance(other,Record):
            return False

        #first we order by type
        mytype=self.type.upper()
        othertype=other.type.upper()
        if mytype!=othertype:
            my_to=self._typeorder(self.type)
            other_to=self._typeorder(other.type)
            return my_to<other_to

        #then by name without the domain, so
        if self.name.lower()!=other.name.lower():
            return self.name<other.name

        #then by content
        if self.content!=other.content:
            return self.content<other.content

        #then by priority/port etc
        if self.modifiers!=other.modifiers:
            return self.modifiers<other.modifiers

        #and finally by ttl
        return self.ttl<other.ttl

    def __eq__(self,other):
        if not isinstance(other,Record):
            return False
        return self.type.upper()==other.type.upper() and self.name.lower()==other.name.lower() and self.zone==other.zone and self.content==other.content and self.priority==other.priority and self.ttl==other.ttl


    def __repr__(self):
        return "<Record  zone=%s name=%s  type=%s modifiers=%s content=%s ttl=%s>"%(self.zone, self.name,self.type," ".join(map(str,self.modifiers)), self.content,self.ttl)

    def __str__(self):
        """Bind style"""
        name=self.name
        if name=='':
            name='@'
        out = "{name}\t{ttl}\tIN\t{typ}\t{mod} {content}".format(name=name,ttl=self.ttl,typ=self.type,mod=" ".join(map(str,self.modifiers)),content=self.content)
        return out
