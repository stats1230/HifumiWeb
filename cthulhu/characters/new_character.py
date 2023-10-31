## packages
import os
import shutil

## カレントディレクトリの設定
try:
    os.chdir('E:\HifumiWeb\cthulhu\characters')
except:
    os.chdir('/home/hifumi/BlackCat/hifumi_web/cthulhu/characters')

## 新しいディレクトリの作成
character_name = input('name of new character')
path = './' + character_name
os.mkdir('./' + character_name)

## 新ディレクトリ内にファイルを作成
open(file = path + '/chatpalette.txt', mode = 'w', encoding = 'utf-8')
shutil.copy('./template/status.json', path)