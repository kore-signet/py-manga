#unfinished - small tool to automatically notify you of the latest manga releases
from pynotifier import Notification
import json
import api
from config_path import ConfigPath
conf_path = ConfigPath('alisw','pymanga','.json')
path = conf_path.readFolderPath()
path.mkdir(parents=True,exist_ok=True)
config_path = path.joinpath('config.json')

if not config_path.exists():
    with open(config_path,'w') as f:
        f.write(json.dumps({
            'ids': [],
            'date_limit': 7
        }))

config = {}
with open(config_path,'r') as f:
    config = json.loads(f.read())

for id in config['ids']:
    series = api.series(id)
    latest = series['latest_releases'][0]
    if int(latest['date'].replace(' days ago','')) < config['date_limit']:
        Notification(
            title='New ' + series['title'] + ' Chapter!',
            description='Chapter ' + latest['chapter'] + ' released.',
            duration=15,
            urgency=Notification.URGENCY_NORMAL
        ).send()
