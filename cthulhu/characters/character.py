import re
import json
import math

name = input('name of the character')
cp     = open(f'./cthulhu/characters/{name}/chatpalette.txt', 'r', encoding='utf-8_sig').read()
with open(f'./cthulhu/characters/{name}/status.json', 'r', encoding='utf-8_sig') as f:
    status = json.load(f)

print(cp)

data = {}
skills = cp.split(sep = '\n')[1:-12]
for skill in skills:
    value      = re.sub(r"\D", "", skill.split(sep = ' ')[0])
    skill_name = re.sub("\【|\】", "", skill.split(sep = ' ')[1])
    data[skill_name] = int(value)

status['status']['HP'] = math.ceil((status['status']['CON'] + status['status']['SIZ']) / 2)
status['status']['MP'] = status['status']['POW']
status['status']['SAN'] = status['status']['POW'] * 5
status['status']['LUCK'] = status['status']['POW'] * 5
status['status']['IDEA'] = status['status']['INT'] * 5
status['status']['KNOWLEGDE'] = status['status']['EDU'] * 5

status['skills'] = data

with open(f'./cthulhu/characters/{name}/status.json', 'w') as f:
    json.dump(status, f, indent=4, ensure_ascii=False)
