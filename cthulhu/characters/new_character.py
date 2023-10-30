## packages
import os

## カレントディレクトリの設定
os.chdir('E:\HifumiWeb\cthulhu\characters')

## 新しいディレクトリの作成
character_name = input('name of new character')
path = './' + character_name
os.mkdir('./' + character_name)

## 新ディレクトリ内にファイルを作成
open(file = path + '/chatpalette.txt', mode = 'w', encoding = 'utf-8')
open(file = path + '/status.csv', mode = 'w',  encoding = 'utf-8')