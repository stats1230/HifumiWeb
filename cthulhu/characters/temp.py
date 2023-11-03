## Initial Settings
import json
import os
import string
from jinja2 import Template
from PyPDF2 import PdfReader, PdfWriter
import shutil

## set current directory
try:
    os.chdir('E:\HifumiWeb\cthulhu')
except:
    os.chdir('/home/hifumi/BlackCat/hifumi_web/cthulhu')

name = input('name of the character: ')
voice = input('CV of the character: ')
with open('./characters/' + name + '/status.json') as f:
    data = json.load(f)

## make pdf sheet
sheet_path = './characters/' + name + '/' + name + '.pdf'
shutil.copy('./characters/template/sheet.pdf', 
            sheet_path)
reader = PdfReader(sheet_path)
existing_page = reader.pages[0]

fields = reader.get_form_text_fields()
fields["職業"] = data['info']['ocupation']
fields["学校・学位"] = ''
fields["出身"] = data['info']['from']
fields["精神的な障害"] = ''
fields["性別"] = data['info']['gender']
fields["年齢"] = data['info']['age']
fields["STR"] = data['status']['STR']
fields["DEX"] = data['status']['DEX']
fields["アイデア"] = data['status']['IDEA']
fields["INT"] = data['status']['INT']
fields["CON"] = data['status']['CON']
fields["APP"] = data['status']['APP']
fields["POW"] = data['status']['POW']
fields["幸運"] = data['status']['LUCK']
fields["SIZ"] = data['status']['SIZ']
fields["SAN"] = data['status']['SAN']
fields["EDU"] = data['status']['EDU']
fields["知識"] = data['status']['KNOWLEGDE']
fields["最大正気度"] = 99 - data['skills']['クトゥルフ神話']
fields["言いくるめ"] = data['skills']['言いくるめ']
fields["医学"] = data['skills']['医学']
fields["運転（自動車）"] = data['skills']['運転']
fields["応急手当"] = data['skills']['応急手当']
fields["オカルト"] = data['skills']['オカルト']
fields["回避"] = data['skills']['回避']
fields["化学"] = data['skills']['化学']
fields["鍵開け"] = data['skills']['鍵開け']
fields["隠す"] = data['skills']['隠す']
fields["隠れる"] = data['skills']['隠れる']
fields["機械修理"] = data['skills']['機械修理']
fields["聞き耳"] = data['skills']['聞き耳']
fields["クトゥルフ神話"] = data['skills']['クトゥルフ神話']
fields["芸術1"] = data['skills']['芸術']
fields["芸術2"] = data['skills']['芸術']
fields["経理"] = data['skills']['経理']
fields["考古学"] = data['skills']['考古学']
fields["コンピューター"] = data['skills']['コンピューター']
fields["忍び歩き"] = data['skills']['忍び歩き']
fields["写真術"] = data['skills']['写真術']
fields["重機械操作"] = data['skills']['重機械操作']
fields["乗馬"] = data['skills']['乗馬']
fields["信用"] = data['skills']['信用']
fields["心理学"] = data['skills']['心理学']
fields["人類学"] = data['skills']['人類学']
fields["水泳"] = data['skills']['水泳']
fields["製作1"] = data['skills']['製作']
fields["製作2"] = data['skills']['製作']
fields["製作3"] = data['skills']['製作']
fields["精神分析"] = data['skills']['精神分析']
fields["生物学"] = data['skills']['生物学']
fields["説得"] = data['skills']['説得']
fields["操縦1"] = data['skills']['操縦']
fields["操縦2"] = data['skills']['操縦']
fields["地質学"] = data['skills']['地質学']
fields["跳躍"] = data['skills']['跳躍']
fields["追跡"] = data['skills']['追跡']
fields["電気修理"] = data['skills']['電気修理']
fields["天文学"] = data['skills']['天文学']
fields["投擲"] = data['skills']['投擲']
fields["登攀"] = data['skills']['登攀']
fields["図書館"] = data['skills']['図書館']
fields["ナビゲート"] = data['skills']['ナビゲート']
fields["値切り"] = data['skills']['値切り']
fields["博物学"] = data['skills']['博物学']
fields["物理学"] = data['skills']['物理学']
fields["変装"] = data['skills']['変装']
fields["法律"] = data['skills']['法律']
fields["母国語"] = data['skills']['母国語']
fields["マーシャルアーツ"] = data['skills']['マーシャルアーツ']
fields["目星"] = data['skills']['目星']
fields["薬学"] = data['skills']['薬学']
fields["歴史"] = data['skills']['歴史']
fields["拳銃"] = data['skills']['拳銃']
fields["サブマシンガン"] = data['skills']['サブマシンガン']
fields["ショットガン"] = data['skills']['ショットガン']
fields["マシンガン"] = data['skills']['マシンガン']
fields["ライフル"] = data['skills']['ライフル']
fields["キック"] = data['skills']['キック']
fields["組みつき"] = data['skills']['組み付き']
fields["こぶし"] = data['skills']['こぶし（パンチ）']
fields["頭突き"] = data['skills']['頭突き']
fields["プレイヤー名"] = voice
fields["探索者名"] = name

for k, v in fields.items():
    if v is None:
        fields[k] = ''

writer = PdfWriter()
writer.update_page_form_field_values(existing_page, fields)
writer.add_page(existing_page)
with open(sheet_path, 'wb') as f:
    writer.write(f)