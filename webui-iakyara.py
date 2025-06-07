import gradio as gr
import requests
from bs4 import BeautifulSoup
import re
import tempfile

# --- iachara.com から情報を抽出するパーサー関数 ---

def parse_iachara_url(url):
    """iachara.comのURLからキャラクターデータを抽出して辞書として返す"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # エラーがあれば例外を発生
    except requests.exceptions.RequestException as e:
        print(f"URLへのアクセスに失敗しました: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    data = {}

    # --- 基本情報 ---
    data['name'] = soup.find('h1').get_text(strip=True)
    data['player'] = soup.select_one('.chara-player a').get_text(strip=True) if soup.select_one('.chara-player a') else 'N/A'
    
    # ファイル名/URL用の英語名を生成
    slug_match = re.search(r'/(\d+)$', url)
    data['slug'] = f"chara_{slug_match.group(1)}" if slug_match else "character"

    base_info_dts = soup.select('#character-base dt')
    for dt in base_info_dts:
        key = dt.get_text(strip=True)
        dd = dt.find_next_sibling('dd')
        if dd:
            if key == "職業": data['occupation'] = dd.get_text(strip=True)
            if key == "出身": data['origin'] = dd.get_text(strip=True)
            if key == "年齢": data['age'] = dd.get_text(strip=True)
            if key == "性別": data['gender'] = dd.get_text(strip=True)
    
    # 身長/体重はddタグにクラスがないため、個別で取得
    height_dd = soup.find('dt', string='身長').find_next_sibling('dd') if soup.find('dt', string='身長') else None
    weight_dd = soup.find('dt', string='体重').find_next_sibling('dd') if soup.find('dt', string='体重') else None
    data['height_weight'] = f"{height_dd.get_text(strip=True)} / {weight_dd.get_text(strip=True)}" if height_dd and weight_dd else "N/A"

    # --- ステータス ---
    status_dts = soup.select('#character-status dt')
    for dt in status_dts:
        key = dt.get_text(strip=True)
        dd = dt.find_next_sibling('dd')
        if dd:
            value = dd.get_text(strip=True)
            data[key.lower()] = value
            if key == "SAN": data['sanity'] = value.split('→')[-1].strip() if '→' in value else value
            if key == "HP": data['hp'] = value
            if key == "MP": data['mp'] = value
    
    # --- 技能 ---
    data['skills'] = {}
    skill_dts = soup.select('#character-skill dt')
    for dt in skill_dts:
        name_full = dt.get_text(strip=True)
        name_clean = re.sub(r'（.+?）', '', name_full).strip()
        dd = dt.find_next_sibling('dd')
        if dd:
            final_value_tag = dd.find('b')
            if final_value_tag:
                data['skills'][name_clean] = int(final_value_tag.get_text(strip=True))

    return data

# --- 前回のスクリプトから流用・改造する部分 ---
SKILL_CATEGORIES = {
    # (省略: 前回のスクリプトと同じなのでコードを短くするため)
    "探索技能": ["応急手当", "鍵開け", "隠す", "隠れる", "聞き耳", "忍び歩き", "写真術", "精神分析", "追跡", "登攀", "図書館", "目星"], "行動技能": ["運転", "機械修理", "重機械操作", "乗馬", "水泳", "製作", "操縦", "跳躍", "電気修理", "ナビゲート", "変装"], "交渉技能": ["言いくるめ", "信用", "説得", "値切り", "母国語"], "戦闘技能": ["回避", "キック", "組み付き", "こぶし", "頭突き", "投擲", "マーシャルアーツ", "拳銃", "サブマシンガン", "ショットガン", "マシンガン", "ライフル"], "知識技能": ["医学", "オカルト", "化学", "クトゥルフ神話", "芸術", "経理", "考古学", "コンピューター", "心理学", "人類学", "生物学", "地質学", "電子工学", "天文学", "博物学", "物理学", "法律", "薬学", "歴史"]
}

def generate_skill_tables_html(skills):
    # (省略: 前回のスクリプトと全く同じ)
    categorized_skills = {cat: [] for cat in SKILL_CATEGORIES}
    for skill_name, skill_value in skills.items():
        for category, skill_list in SKILL_CATEGORIES.items():
            if skill_name in skill_list: categorized_skills[category].append((skill_name, skill_value)); break
    html = '<div class="grid__wrapper">\n'
    columns = [("探索技能", ["探索技能"]), ("行動・交渉技能", ["行動技能", "交渉技能"]), ("知識技能", ["知識技能"]), ("戦闘技能", ["戦闘技能"])]
    for _, cat_names in columns:
        html += f'  <div class="grid__item">\n'
        for cat_name in cat_names:
            skill_list = categorized_skills.get(cat_name, [])
            if skill_list:
                html += f'    <h3>{cat_name}</h3>\n<table class="skill-table">\n'
                for name, value in skill_list: html += f'        <tr><td class="skill-key">{name}</td><td class="skill-value">{value}</td></tr>\n'
                html += '    </table>\n'
        html += '  </div>\n'
    html += '</div>'
    return html

# --- メイン処理関数 ---

def process_url_and_generate_file(url):
    """URLを処理してMarkdownファイルを生成し、そのパスを返す"""
    if not url or "iachara.com" not in url:
        raise gr.Error("有効なiachara.comのURLを入力してください。")
    
    # Webページからデータを抽出
    char_data = parse_iachara_url(url)
    if not char_data:
        raise gr.Error("キャラクター情報の取得に失敗しました。URLが正しいか確認してください。")

    # サイドバーのテキスト部分を作成
    sidebar_text = (
        f"<strong>プレイヤー:</strong> {char_data.get('player', 'N/A')}<br>"
        f"<strong>職業:</strong> {char_data.get('occupation', 'N/A')}<br>"
        f"<strong>出身:</strong> {char_data.get('origin', 'N/A')}<br>"
        f"<strong>年齢:</strong> {char_data.get('age', 'N/A')}<br>"
        f"<strong>性別:</strong> {char_data.get('gender', 'N/A')}<br>"
        f"<strong>身長/体重:</strong> {char_data.get('height_weight', 'N/A')}"
    )
    
    # スキルテーブルのHTMLを生成
    skill_tables_html = generate_skill_tables_html(char_data.get('skills', {}))
    
    # Markdownテンプレート
    content = f"""---
title: "探索者：{char_data.get('name', '無名')}"
layout: single
permalink: /cthulhu/characters/{char_data.get('slug', 'character')}/
sidebar:
  - title: "{char_data.get('name', '無名')}"
    image: /assets/images/coc-character/{char_data.get('slug', 'character')}.png
    image_alt: "{char_data.get('name', '無名')}の画像"
    text: "{sidebar_text}"
---

## 探索者のステータス

**HP**: {char_data.get('hp', 'N/A')}, **MP**: {char_data.get('mp', 'N/A')}, **正気度**: {char_data.get('sanity', 'N/A')}

**STR**: {char_data.get('str', 'N/A')}, **CON**: {char_data.get('con', 'N/A')}, **POW**: {char_data.get('pow', 'N/A')}, **DEX**: {char_data.get('dex', 'N/A')}, **APP**: {char_data.get('app', 'N/A')}, **SIZ**: {char_data.get('siz', 'N/A')}, **INT**: {char_data.get('int', 'N/A')}, **EDU**: {char_data.get('edu', 'N/A')},

 **幸運**: {char_data.get('幸運', 'N/A')}, **アイデア**: {char_data.get('アイデア', 'N/A')}, **知識**: {char_data.get('知識', 'N/A')}

## 探索者の技能

{skill_tables_html}
"""
    
    # 一時ファイルとして保存してダウンロードリンクを生成
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.md', prefix=f"{char_data.get('slug', 'character')}_") as temp_file:
        temp_file.write(content)
        return temp_file.name

# --- Gradioインターフェースの定義 ---

with gr.Blocks(title="iachara→Markdownジェネレーター") as demo:
    gr.Markdown("# iacharaキャラクターシート → Jekyll用Markdownジェネレーター")
    gr.Markdown("iachara.comのキャラクターページのURLを貼り付けて「生成」ボタンを押してください。")
    
    url_in = gr.Textbox(label="iachara.com キャラクターURL", placeholder="https://iachara.com/view/...")
    submit_btn = gr.Button("Markdownファイルを生成", variant="primary")
    output_file = gr.File(label="生成されたMarkdownファイル")

    submit_btn.click(
        fn=process_url_and_generate_file,
        inputs=url_in,
        outputs=output_file
    )

# --- Web UIの起動 ---
if __name__ == "__main__":
    demo.launch()