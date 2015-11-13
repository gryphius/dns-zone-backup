from dnsmadeeasy import DMEApi
from powerdnsnet import PDNSNetApi
from axfr import AXFR
PROVIDERS = {
    'dnsmadeeasy':DMEApi,
    'powerdnsnet':PDNSNetApi,
    'axfr':AXFR,
}


