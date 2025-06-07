import gradio as gr
import re
import os
import tempfile

# --- 前回のスクリプトから流用する部分 ---

# スキルをカテゴリに分類するためのリスト
SKILL_CATEGORIES = {
    "探索技能": ["応急手当", "鍵開け", "隠す", "隠れる", "聞き耳", "忍び歩き", "写真術", "精神分析", "追跡", "登攀", "図書館", "目星"],
    "行動技能": ["運転", "機械修理", "重機械操作", "乗馬", "水泳", "製作", "操縦", "跳躍", "電気修理", "ナビゲート", "変装"],
    "交渉技能": ["言いくるめ", "信用", "説得", "値切り", "母国語"],
    "戦闘技能": ["回避", "キック", "組み付き", "こぶし", "頭突き", "投擲", "マーシャルアーツ", "拳銃", "サブマシンガン", "ショットガン", "マシンガン", "ライフル"],
    "知識技能": ["医学", "オカルト", "化学", "クトゥルフ神話", "芸術", "経理", "考古学", "コンピューター", "心理学", "人類学", "生物学", "地質学", "電子工学", "天文学", "博物学", "物理学", "法律", "薬学", "歴史"]
}

def parse_skill_text(skill_text):
    """テキストからスキル辞書と正気度を返す"""
    skills = {}
    sanity = "N/A"
    for line in skill_text.strip().split('\n'):
        san_match = re.search(r'1d100<={(\d+)}\s*【正気度ロール】', line)
        if san_match:
            sanity = san_match.group(1)
            continue
        skill_match = re.search(r'CCB<=(\d+)\s*【(.+?)】', line)
        if skill_match:
            value = int(skill_match.group(1))
            name_full = skill_match.group(2)
            name_clean = re.sub(r'（.+?）', '', name_full).strip()
            skills[name_clean] = value
    return skills, sanity

def generate_skill_tables_html(skills):
    """スキル辞書からカテゴリ分けされたHTMLテーブルを生成する"""
    categorized_skills = {cat: [] for cat in SKILL_CATEGORIES}
    for skill_name, skill_value in skills.items():
        for category, skill_list in SKILL_CATEGORIES.items():
            if skill_name in skill_list:
                categorized_skills[category].append((skill_name, skill_value))
                break
    
    html = '<div class="grid__wrapper">\n'
    # カラムの定義（koyama-mamoru.mdのレイアウトに基づく）
    columns = [
        ("探索技能", ["探索技能"]),
        ("行動・交渉技能", ["行動技能", "交渉技能"]),
        ("知識技能", ["知識技能"]),
        ("戦闘技能", ["戦闘技能"]),
    ]
    
    for col_title, cat_names in columns:
        html += f'  <div class="grid__item">\n'
        for cat_name in cat_names:
            skill_list = categorized_skills.get(cat_name, [])
            if skill_list:
                html += f'    <h3>{cat_name}</h3>\n'
                html += '    <table class="skill-table">\n'
                for name, value in skill_list:
                    html += f'        <tr><td class="skill-key">{name}</td><td class="skill-value">{value}</td></tr>\n'
                html += '    </table>\n'
        html += '  </div>\n'
        
    html += '</div>'
    return html

# --- Web UIのためのメイン関数 ---

def generate_character_md(
    name, player, slug, occupation, origin, age, gender, height_weight,
    hp, mp, san_initial,
    str_val, con_val, pow_val, dex_val, app_val, siz_val, int_val, edu_val,
    skill_text
):
    """全ての情報を受け取り、Markdownファイルを生成してそのパスを返す"""
    
    # スキルと正気度を解析
    skills, sanity_from_file = parse_skill_text(skill_text)
    sanity = sanity_from_file if sanity_from_file != "N/A" else san_initial

    # 計算値を設定
    luck = int(pow_val) * 5
    idea = int(int_val) * 5
    knowledge = int(edu_val) * 5
    
    # サイドバーのテキスト部分を作成
    sidebar_text = (
        f"<strong>プレイヤー:</strong> {player}<br>"
        f"<strong>職業:</strong> {occupation}<br>"
        f"<strong>出身:</strong> {origin}<br>"
        f"<strong>年齢:</strong> {age}<br>"
        f"<strong>性別:</strong> {gender}<br>"
        f"<strong>身長/体重:</strong> {height_weight}"
    )

    # スキルテーブルのHTMLを生成
    skill_tables_html = generate_skill_tables_html(skills)
    
    # Markdownテンプレート
    content = f"""---
title: "探索者：{name}"
layout: single
permalink: /cthulhu/characters/{slug}/
sidebar:
  - title: "{name}"
    image: /assets/images/coc-character/{slug}.png
    image_alt: "{name}の画像"
    text: "{sidebar_text}"
---

## 探索者のステータス

**HP**: {hp}, **MP**: {mp}, **正気度**: {sanity}

**STR**: {str_val}, **CON**: {con_val}, **POW**: {pow_val}, **DEX**: {dex_val}, **APP**: {app_val}, **SIZ**: {siz_val}, **INT**: {int_val}, **EDU**: {edu_val},

 **幸運**: {luck}, **アイデア**: {idea}, **知識**: {knowledge}

## 探索者の技能

{skill_tables_html}
"""
    
    # 一時ファイルとして保存して、Gradioがダウンロードリンクを生成できるようにする
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.md', prefix=f'{slug}_') as temp_file:
        temp_file.write(content)
        return temp_file.name

# --- Gradioインターフェースの定義 ---

with gr.Blocks(title="キャラクターシートジェネレーター") as demo:
    gr.Markdown("# キャラクターシートジェネレーター for Minimal Mistakes")
    gr.Markdown("キャラクターの情報を入力し、スキルリストを貼り付けて「生成」ボタンを押してください。")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 基本情報")
            name_in = gr.Textbox(label="キャラクター名")
            player_in = gr.Textbox(label="プレイヤー名")
            slug_in = gr.Textbox(label="ファイル名/URL用の英語名", placeholder="例: kouyama-mamoru")
            
            gr.Markdown("### サイドバー情報")
            occupation_in = gr.Textbox(label="職業")
            origin_in = gr.Textbox(label="出身")
            age_in = gr.Number(label="年齢", value=30)
            gender_in = gr.Textbox(label="性別")
            height_weight_in = gr.Textbox(label="身長/体重", placeholder="例: 182cm / 70kg")

        with gr.Column():
            gr.Markdown("### ステータス")
            with gr.Row():
                hp_in = gr.Number(label="HP", value=15)
                mp_in = gr.Number(label="MP", value=9)
                san_in = gr.Number(label="初期正気度", value=45)
            with gr.Row():
                str_in = gr.Number(label="STR", value=10)
                con_in = gr.Number(label="CON", value=15)
                pow_in = gr.Number(label="POW", value=9)
                dex_in = gr.Number(label="DEX", value=10)
            with gr.Row():
                app_in = gr.Number(label="APP", value=13)
                siz_in = gr.Number(label="SIZ", value=15)
                int_in = gr.Number(label="INT", value=15)
                edu_in = gr.Number(label="EDU", value=17)

    gr.Markdown("### スキルリスト")
    skill_text_in = gr.Textbox(label="スキルtxtの内容をここに貼り付け", lines=15, placeholder="CCB<=80 【アイデア】\nCCB<=70 【幸運】\n...")
    
    submit_btn = gr.Button("Markdownファイルを生成", variant="primary")
    output_file = gr.File(label="生成されたMarkdownファイル")

    submit_btn.click(
        fn=generate_character_md,
        inputs=[
            name_in, player_in, slug_in, occupation_in, origin_in, age_in, gender_in, height_weight_in,
            hp_in, mp_in, san_in,
            str_in, con_in, pow_in, dex_in, app_in, siz_in, int_in, edu_in,
            skill_text_in
        ],
        outputs=output_file
    )

# --- Web UIの起動 ---
if __name__ == "__main__":
    demo.launch()