#!/usr/bin/env python3
from sanic import Sanic
from sanic.response import json as sanic_json
from ip_scanner.scanner import IPScanner
from asset_manager_driver.driver import AssetDriver
from scheduler.app_scheduler import Scheduler
from config.config import get_config
from threading import Thread
from utils.utils import get_main_logger, dmsg, get_args

tools = {}
options = get_args()
MODE = 'DEV'
print(options.mode)
if options.mode:
    MODE = ('DEV' if options.mode == 'dev' else 'PROD')
else:
    MODE = 'DEV'


def setup_module(mode='DEV'):
    tools['app'] = Sanic(__name__)
    tools['log'] = get_main_logger('main.py')
    c = tools['conf'] = get_config()
    s = tools['scan'] = IPScanner()
    d = tools['driver'] = AssetDriver(c[mode]['asset_host'], c[mode]['asset_port'])
    sc = tools['sched'] = Scheduler()
    # setup the scanning function # 'day_of_week': 'mon-fri',
    sc.add_cron_job(s.scan_all, {'id': c[mode]['scan_id'], 'hour': 1, 'minute': 0})
    # setup the update function # 'day_of_week': 'mon-fri',
    sc.add_cron_job(d.update_asset_repo, {'id': c[mode]['update_id'], 'hour': 3, 'minute': 0})
    sc.start_sched_jobs()
    return tools


setup_module(mode=MODE)
app = tools['app']


@app.get("/")
async def home(request):
    tools['log'].info(dmsg('') + ' This is the IPScanner home endpoint.')
    return sanic_json({"message": ' This is the IPScanner home endpoint.'}), 200


@app.get('/health')
async def health(request):
    return sanic_json({'result': 'This is the IP scanner component'}, status=200)


@app.get("/scan")
async def scan(request):
    tools['log'].info('Starting network scan...')
    Thread(target=tools['scan'].scan_all).start()
    return sanic_json({"message": " started scanning."}, 200)


@app.get("/update")
async def update(request):
    tools['log'].info('Updating entities in asset manager...')
    Thread(target=tools['driver'].update_asset_repo).start()
    return sanic_json({"message": "Starting updating."}, 200)


if __name__ == '__main__':
    # tools['log'].info('Starting network scan...')
    # Thread(target=tools['scan'].scan_all).start()
    # tools['log'].info('Updating entities in asset manager...')
    # tools['driver'].update_asset_repo()
    app.run(host="0.0.0.0", port=8001)
