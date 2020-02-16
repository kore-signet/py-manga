#unfinished - small tool to automatically notify you of the latest manga releases

import json
import pymanga
from config_path import ConfigPath
conf_path = ConfigPath('alisw','pymanga','.json')
path = conf_path.readFolderPath().joinpath('config.json')

if path is None:
    path = conf_path.saveFolderPath(mkdir=true)
    config_path = path.joinpath('config.json')
    with f = open(config_path,'w'):
        f.write(json.dumps({
            'ids': [],
            'date_limit': '7'
        }))

config = {}
with f = open(config_path,'r'):
    config = json.loads(f.read())

for id in config['ids']:
    series = pymanga.series(id)
