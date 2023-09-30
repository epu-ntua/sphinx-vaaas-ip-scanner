from file_utils.file_parser import get_files
import json
from utils.utils import get_main_logger, dmsg, is_json
from request_mapper.http_client import HttpClient
import requests
from datetime import datetime
from redis_manager.manager import RedisManager

log = get_main_logger()


class AssetDriver:
    def __init__(self, asset_host=None, asset_host_port=None):
        self.host = asset_host
        self.port = asset_host_port
        self.new_ips = {}
        self.current_ip = None
        self.searchUrl = 'entities/search/'
        self.addIpUrl = 'entities'
        self.db = RedisManager()

    def handle_res(self, _resp: requests.models.Response, *args, **kwargs):
        # log.info(f'Received response from {_resp.url} with content-> {_resp.content}')
        response = json.loads(_resp.content)
        if (_resp.status_code == 200) and (response['message']['result'] == 'SEARCH_ENTITY_FAIL'):
            # print(_resp.status_code)
            pass
        elif (_resp.status_code == 200) and (response['message']['result'] == 'SEARCH_ENTITY_SUCCESS'):
            pass

    def handle_req(self, _req: requests.models.Request, *args, **kwargs):
        # print(_req.url)
        log.info(f'{str(_req.method).upper()} request for URL: {_req.url}')

    def handle_errors(self, _resp: requests.models.Response, *args, **kwargs):
        _resp.raise_for_status()
        log.error(f'Response contained errors-> Status Code: {_resp.status_code}')

    def get_asset_hosts(self, _assets):
        temp = {}
        temp_asset = {}
        for asset in _assets:
            for i, j in asset.items():
                for k, v in j.items():
                    if k != 'stats' and k != 'runtime':
                        # print(v)
                        if v['macaddress']:
                            temp[k] = {'ip': k, 'mac': v['macaddress']['addr']}
                            if 'vendor' in v['macaddress']:
                                temp[k] = {'ip': k, 'mac': v['macaddress']['addr'], 'vendor': v['macaddress']['vendor']}
                        temp_asset.update(temp)
        return temp_asset

    def update_asset_repo(self):
        try:
            c = HttpClient()
            assets = get_files()
            # print(assets)
            all_hosts = self.get_asset_hosts(assets) if assets else {}
            # all_hosts = {k: {'ip': k, 'mac': v['macaddress']['addr'], 'vendor': v['macaddress']['vendor']} for (i, j) in assets.items() for (k, v) in j.items() if v['macaddress'] if (k != 'stats') and (k != 'runtime')}
            # all_hosts = {v['hostname']: {"ip": v['hostname'], "mac": v['mac']} for asset in assets for (net, values) in asset.items() for k, v in values.items()}
            # print(all_hosts)
            ## reqs = [c.singleRequest('POST', f'http://{self.host}:{self.port}/{self.searchUrl}', host) for host in all_hosts.values()]
            for host in all_hosts.values():
                req = c.singleRequest('POST', f'http://{self.host}:{self.port}/{self.searchUrl}', host)
                # req = c.singleRequest('GET', f'http://10.0.1.220:8888/')
                log.debug(dmsg('') + 'Search Results: ' + str(req))
                if req.content and is_json(req.content):
                    if json.loads(req.content)['message']['result'] != 'SEARCH_ENTITY_SUCCESS':
                        req2 = c.singleRequest('POST', f'http://{self.host}:{self.port}/{self.addIpUrl}', host)
                        if req2.content and is_json(req2.content):
                            log.debug(req2.content)
                        else:
                            log.error(dmsg('') + f'Request POST => http://{self.host}:{self.port}/{self.addIpUrl} did not pull through')
                    else:
                        log.debug(dmsg('') + 'ENTITY ALREADY EXISTS')
                else:
                    log.error(dmsg('') + f'Search request result for host {host} was not serializable')
        #################################################################################################################################################################
        #     #     # print(dmsg(''), reqs[0].url)
        # if reqs:
        #     results = c.mapRequests(reqs)
        #     wait_until(results)  # will wait until results are not None
        #     log.debug(dmsg('') + 'Search Results: ' + str(results))
        #     if results:
        #         self.new_ips = dict(zip(all_hosts, [(False if json.loads(r.content)['message']['result'] == 'SEARCH_ENTITY_SUCCESS' else True) for r in results if r and is_json(r.content)]))
        #         self.new_ips = {k: v for k, v in self.new_ips.items() if v is not False}
        #         reqs_new_ips = [c.singleRequest('POST', f'http://{self.host}:{self.port}/{self.addIpUrl}', all_hosts[ip]) for ip in self.new_ips.keys()]
        #         if reqs_new_ips:
        #             results_new = c.mapRequests(reqs_new_ips)
        #             wait_until(results_new)  # will wait until results are not None
        #             log.debug(dmsg('') + 'Update Results: ' + str(results_new))
        #             print([json.loads(r.content) for r in results_new])
        #         else:
        #             log.debug(dmsg('') + ' Did not perform any request. Probably no new IPs were found.')
        # else:
        #     log.debug(dmsg('') + 'Results were either null or empty')
        # else:
        #     log.debug(dmsg('') + ' Did not perform any request. Probably no new IPs were found.')

        except Exception as e:
            log.exception(dmsg('') + 'Something went wrong. Error: ' + e.__str__())


# a = AssetDriver(asset_host='127.0.0.1', asset_host_port=8002)
# a.update_asset_repo()


class Entity:
    def __init__(self, id='', name='', description='', assetType='', assessed=False, cvss=0.0, status=False, sensitivity=0, location='', owner='', backupLocation='', dependedServices=None,
                 active=True, assetValue='',
                 ip='', mac='', vendor=''):
        if dependedServices is None:
            dependedServices = []
        self.id = id
        self.name = name
        self.description = description
        self.assetType = assetType
        self.assessed = assessed
        self.cvss = cvss
        self.modified = datetime.now()
        self.status = status
        self.sensitivity = sensitivity
        self.location = location
        self.owner = owner
        self.backupLocation = backupLocation
        self.dependedServices = dependedServices
        self.assetValue = assetValue
        self.active = active
        self.ip = ip
        self.mac = mac
        self.vendor = vendor

    def update(self, id='', name='', description='', assetType='', assessed=False, cvss=0.0, status=False, sensitivity=0, location='', owner='', backupLocation='', dependedServices=None,
               active=True, assetValue='',
               ip='', mac='', vendor=''):
        self.id = id if not self.id else self.id
        self.name = name if not self.name else self.name
        self.description = description if not self.description else self.description
        self.assetType = assetType if not self.assetType else self.assetType
        self.assessed = assessed if not self.assessed else self.assessed
        self.cvss = cvss if not self.cvss else self.cvss
        self.modified = datetime.now()
        self.status = status if not self.status else self.status
        self.sensitivity = sensitivity if not self.sensitivity else self.sensitivity
        self.location = location if not self.location else self.location
        self.owner = owner if not self.owner else self.owner
        self.backupLocation = backupLocation if not self.backupLocation else self.backupLocation
        self.dependedServices = dependedServices if not self.dependedServices else self.dependedServices
        self.active = active if not self.active else self.active
        self.assetValue = assetValue if not self.assetValue else self.assetValue
        self.ip = ip if not self.ip else self.ip
        self.mac = mac if not self.mac else self.mac
        self.vendor = vendor if not self.vendor else self.vendor
