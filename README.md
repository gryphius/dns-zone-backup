dns zone backup
---------------

This script makes local file backups from dns zones hosted on various external providers.

This is not yet ready for production, there are a lot of places where the script will mess up trailing dots, relative hostnames etc.


| provider     | description                              | status   |
| ------------ | ---------------------------------------- | -------- |
| powerdnsapi  | powerdns HTTP API                        | planned  |
| powerdnssql  | powerdns SQL Database                    | planned  |
| powerdnsnet  | powerdns.net SOAP API                    | beta     |
| axfr         | AXFR                                     | beta     |
| dnsmadeeasy  | dnsmadeeasy.com REST API                 | beta     |

configuration file example

```
[DEFAULT]
filetemplate=/home/bob/my-dns-zones/${provider}/${zonename}.txt

[pdnsnet]
enabled=yes
provider=powerdnsnet
apikey=xxx-xxx-xxxx

[axfr]
enabled=yes
provider=axfr
server=axfr1.dnsmadeeasy.com
zones=example.com,example.net,example.org

[dnsmadeeasy]
enabled=yes
provider=dnsmadeeasy
apikey=xxx-xxx-xxx
secret=yyy-yyy-yyy
filetemplate=/home/bob/other-dns-zones/${zonename}.txt

```