from flask import Flask, render_template, jsonify, request, send_from_directory
import pytchat
import threading
import random
import time
import json
import os
import re

app = Flask(__name__)

# Данные розыгрыша
giveaway = {
    "video_id": "",
    "keyword": "",
    "accept_any_message": False,
    "participants": [],
    "participants_data": {},
    "winner": None,
    "winner_avatar": None,
    "winner_messages": [],
    "winner_picked_at": None,
    "winner_first_message_at": None,
    "is_active": False,
    "is_connected": False,
    "countdown": 0
}

# Настройки виджета по умолчанию
default_widget_settings = {
    "width": 400,
    "height": 50,
    "border_radius": 10,
    
    "font_size_label": 20,
    "font_size_keyword": 20,
    "font_size_separator": 20,
    "font_size_count": 20,
    "font_size_countdown": 48,
    "font_size_winner_label": 20,
    "font_size_winner_name": 20,
    "font_size_timer": 16,
    
    "text_label": "✍️ Пиши в чат:",
    "text_separator": "|",
    "text_count_suffix": "👥",
    "text_winner_label_start": "🏆 Победитель:",
    "text_winner_label_end": "🏆",
    "text_timer_prefix": "⏱️",
    
    "show_label": True,
    "show_keyword": True,
    "show_separator": True,
    "show_count": True,
    "show_winner_label_start": True,
    "show_winner_label_end": True,
    "show_winner_name": True,
    "show_winner_avatar": True,
    "show_timer": True,
    
    "bg_type_active": "gradient",
    "bg_color_1": "#667eea",
    "bg_color_2": "#764ba2",
    "bg_image_active": "",
    "bg_type_winner": "gradient",
    "winner_bg_1": "#f39c12",
    "winner_bg_2": "#e74c3c",
    "bg_image_winner": "",
    
    "text_color_label": "#ffffff",
    "text_color_keyword": "#ffffff",
    "text_color_separator": "#ffffff",
    "text_color_count": "#ffffff",
    "text_color_countdown": "#ffffff",
    "text_color_winner_label": "#ffffff",
    "text_color_winner_name": "#ffffff",
    "text_color_timer": "#ffffff",
    "keyword_bg_color": "rgba(255,255,255,0.2)",
    
    "winner_info_bg_enabled": False,
    "winner_info_bg_color": "rgba(0,0,0,0.3)",
    
    "text_stroke_enabled": False,
    "text_stroke_color": "#000000",
    "text_stroke_width": 1,
    "text_shadow_enabled": False,
    "text_shadow_color": "#000000",
    "text_shadow_x": 2,
    "text_shadow_y": 2,
    "text_shadow_blur": 4,
    
    "winner_avatar_size": 40,
    "winner_avatar_border_radius": 50
}

widget_settings = default_widget_settings.copy()

saved_channel = {
    "channel_id": ""
}

chat_thread = None
stop_flag = False
chat_instance = None


def load_settings():
    global widget_settings
    if os.path.exists('widget_settings.json'):
        try:
            with open('widget_settings.json', 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                widget_settings = {**default_widget_settings, **loaded}
        except:
            widget_settings = default_widget_settings.copy()
    else:
        widget_settings = default_widget_settings.copy()


def save_settings():
    with open('widget_settings.json', 'w', encoding='utf-8') as f:
        json.dump(widget_settings, f, ensure_ascii=False, indent=2)


def load_channel():
    global saved_channel
    if os.path.exists('channel.json'):
        try:
            with open('channel.json', 'r', encoding='utf-8') as f:
                saved_channel = json.load(f)
        except:
            pass


def save_channel():
    with open('channel.json', 'w', encoding='utf-8') as f:
        json.dump(saved_channel, f, ensure_ascii=False)


def get_live_video_id(channel_input):
    import urllib.request
    import urllib.error
    
    channel_input = channel_input.strip()
    
    if re.match(r'^[a-zA-Z0-9_-]{11}$', channel_input):
        return channel_input
    
    if channel_input.startswith('@'):
        live_url = f"https://www.youtube.com/{channel_input}/live"
    elif 'youtube.com' in channel_input:
        channel_input = channel_input.replace('/live', '').rstrip('/')
        live_url = f"{channel_input}/live"
    elif channel_input.startswith('UC'):
        live_url = f"https://www.youtube.com/channel/{channel_input}/live"
    else:
        live_url = f"https://www.youtube.com/@{channel_input}/live"
    
    try:
        print(f"🔍 Ищу стрим: {live_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(live_url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
            match = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            if match:
                video_id = match.group(1)
                print(f"✅ Найден стрим: {video_id}")
                return video_id
            
            match = re.search(r'watch\?v=([a-zA-Z0-9_-]{11})', html)
            if match:
                video_id = match.group(1)
                print(f"✅ Найден стрим: {video_id}")
                return video_id
                
    except Exception as e:
        print(f"❌ Ошибка поиска стрима: {e}")
    
    return None


def get_author_info(message):
    author = message.author
    
    name = None
    if hasattr(author, 'displayName') and author.displayName:
        name = author.displayName
    elif hasattr(author, 'name') and author.name:
        name = author.name
    elif hasattr(author, 'channelName') and author.channelName:
        name = author.channelName
    
    if not name:
        name = "Unknown"
    
    if name.startswith('@'):
        alternatives = ['displayName', 'channelName', 'title', 'authorName']
        for attr in alternatives:
            if hasattr(author, attr):
                alt_name = getattr(author, attr, None)
                if alt_name and not alt_name.startswith('@'):
                    name = alt_name
                    break
    
    avatar = None
    if hasattr(author, 'imageUrl') and author.imageUrl:
        avatar = author.imageUrl
    elif hasattr(author, 'profileImage') and author.profileImage:
        avatar = author.profileImage
    elif hasattr(author, 'avatar') and author.avatar:
        avatar = author.avatar
    
    return name, avatar


load_settings()
load_channel()


def watch_chat():
    global giveaway, stop_flag, chat_instance
    
    try:
        chat_instance = pytchat.create(video_id=giveaway["video_id"], interruptable=False)
        giveaway["is_connected"] = True
        print(f"✅ Подключился к чату: {giveaway['video_id']}")
        
        while chat_instance.is_alive() and not stop_flag:
            try:
                items = chat_instance.get()
                for message in items.sync_items():
                    author, avatar = get_author_info(message)
                    text = message.message
                    
                    if giveaway["winner"] and author == giveaway["winner"]:
                        if giveaway["winner_first_message_at"] is None:
                            giveaway["winner_first_message_at"] = time.time()
                            print(f"⏱️ Победитель ответил! Время: {time.time() - giveaway['winner_picked_at']:.1f} сек")
                        
                        giveaway["winner_messages"].append({
                            "time": time.strftime("%H:%M:%S"),
                            "text": text
                        })
                        giveaway["winner_messages"] = giveaway["winner_messages"][-50:]
                        print(f"💬 {author}: {text}")
                    
                    keyword_ok = giveaway["keyword"].lower() in text.lower() if giveaway["keyword"] else False
                    accept_by_mode = giveaway.get("accept_any_message", False) or keyword_ok
                    # После выбора победителя is_active=False, но чат живёт — продолжаем принимать новых по ключу (для реролла).
                    session_collecting = giveaway["is_active"] or bool(giveaway.get("winner"))
                    if session_collecting and accept_by_mode:
                        if author not in giveaway["participants"]:
                            giveaway["participants"].append(author)
                            giveaway["participants_data"][author] = {"avatar": avatar}
                            print(f"✅ {author} участвует! (Всего: {len(giveaway['participants'])})")
                            
            except Exception as e:
                print(f"Ошибка чтения: {e}")
            
            time.sleep(0.5)
                        
    except Exception as e:
        print(f"Ошибка чата: {e}")
    finally:
        giveaway["is_connected"] = False
        print("❌ Отключился от чата")


# === СТРАНИЦЫ ===

@app.route('/')
def admin():
    return render_template('admin.html')


@app.route('/obs-dock')
def obs_dock():
    return render_template('obs_dock.html')


@app.route('/widget')
def widget():
    return render_template('widget.html')


@app.route('/constructor')
def constructor():
    return render_template('constructor.html')

@app.route('/wheel-integration')
def wheel_integration():
    return render_template('wheel_integration.html')


@app.route('/fonts/<path:filename>')
def serve_font(filename):
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    local_font = os.path.join(fonts_dir, filename)
    if os.path.exists(local_font):
        return send_from_directory(fonts_dir, filename)

    # Fallback: общие шрифты из корня проекта / assets/fonts.
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for sub in ("", os.path.join("assets", "fonts")):
        base = root_dir if sub == "" else os.path.join(root_dir, sub)
        candidate = os.path.join(base, filename)
        if os.path.exists(candidate):
            return send_from_directory(base, filename)

    return jsonify({"error": "Font not found"}), 404


@app.route('/images/<path:filename>')
def serve_image(filename):
    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
    return send_from_directory(images_dir, filename)


# === API РОЗЫГРЫША ===

@app.route('/api/status')
def status():
    timer_seconds = None
    timer_stopped = False
    
    if giveaway["winner_picked_at"]:
        if giveaway["winner_first_message_at"]:
            timer_seconds = giveaway["winner_first_message_at"] - giveaway["winner_picked_at"]
            timer_stopped = True
        else:
            timer_seconds = time.time() - giveaway["winner_picked_at"]
            timer_stopped = False
    
    return jsonify({
        "video_id": giveaway["video_id"],
        "keyword": giveaway["keyword"],
        "accept_any_message": giveaway.get("accept_any_message", False),
        "participants": giveaway["participants"],
        "participants_data": giveaway["participants_data"],
        "count": len(giveaway["participants"]),
        "winner": giveaway["winner"],
        "winner_avatar": giveaway["winner_avatar"],
        "winner_messages": giveaway["winner_messages"],
        "is_active": giveaway["is_active"],
        "is_connected": giveaway["is_connected"],
        "countdown": giveaway["countdown"],
        "timer_seconds": timer_seconds,
        "timer_stopped": timer_stopped
    })


@app.route('/api/start', methods=['POST'])
def start():
    global chat_thread, giveaway, stop_flag
    
    data = request.json
    channel_input = data.get("channel", "")
    
    video_id = get_live_video_id(channel_input)
    
    if not video_id:
        return jsonify({"success": False, "error": "Не удалось найти активный стрим на этом канале"})
    
    stop_flag = False
    giveaway["video_id"] = video_id
    giveaway["keyword"] = data.get("keyword", "")
    giveaway["accept_any_message"] = bool(data.get("accept_any_message", False))
    giveaway["participants"] = []
    giveaway["participants_data"] = {}
    giveaway["winner"] = None
    giveaway["winner_avatar"] = None
    giveaway["winner_messages"] = []
    giveaway["winner_picked_at"] = None
    giveaway["winner_first_message_at"] = None
    giveaway["is_active"] = True
    giveaway["countdown"] = 0
    
    mode_text = "любое сообщение" if giveaway["accept_any_message"] else f"слово: {giveaway['keyword']}"
    print(f"🎲 Розыгрыш запущен! Режим: {mode_text}")
    
    chat_thread = threading.Thread(target=watch_chat, daemon=True)
    chat_thread.start()
    
    return jsonify({"success": True, "video_id": video_id})


@app.route('/api/stop', methods=['POST'])
def stop():
    global stop_flag
    stop_flag = True
    giveaway["is_active"] = False
    giveaway["countdown"] = 0
    print("⏹️ Розыгрыш остановлен")
    return jsonify({"success": True})


@app.route('/api/pick', methods=['POST'])
def pick():
    global giveaway
    
    if not giveaway["participants"]:
        return jsonify({"success": False, "error": "Нет участников"})
    
    def countdown_and_pick():
        for i in [3, 2, 1]:
            giveaway["countdown"] = i
            time.sleep(1)
        
        giveaway["countdown"] = 0
        winner = random.choice(giveaway["participants"])
        giveaway["winner"] = winner
        giveaway["winner_avatar"] = giveaway["participants_data"].get(winner, {}).get("avatar")
        giveaway["winner_messages"] = []
        giveaway["winner_picked_at"] = time.time()
        giveaway["winner_first_message_at"] = None
        giveaway["is_active"] = False
        print(f"🎉 Победитель: {giveaway['winner']}")
    
    thread = threading.Thread(target=countdown_and_pick, daemon=True)
    thread.start()
    
    return jsonify({"success": True})


@app.route('/api/reroll', methods=['POST'])
def reroll():
    global giveaway
    
    if not giveaway["participants"] or not giveaway["winner"]:
        return jsonify({"success": False, "error": "Нет победителя для реролла"})
    
    old_winner = giveaway["winner"]
    if old_winner in giveaway["participants"]:
        giveaway["participants"].remove(old_winner)
    if old_winner in giveaway["participants_data"]:
        del giveaway["participants_data"][old_winner]
    
    if not giveaway["participants"]:
        return jsonify({"success": False, "error": "Больше нет участников"})
    
    def countdown_and_reroll():
        for i in [3, 2, 1]:
            giveaway["countdown"] = i
            time.sleep(1)
        
        giveaway["countdown"] = 0
        winner = random.choice(giveaway["participants"])
        giveaway["winner"] = winner
        giveaway["winner_avatar"] = giveaway["participants_data"].get(winner, {}).get("avatar")
        giveaway["winner_messages"] = []
        giveaway["winner_picked_at"] = time.time()
        giveaway["winner_first_message_at"] = None
        print(f"🔄 Реролл! Новый победитель: {giveaway['winner']}")
    
    thread = threading.Thread(target=countdown_and_reroll, daemon=True)
    thread.start()
    
    return jsonify({"success": True, "old_winner": old_winner})


@app.route('/api/giveaway-update', methods=['POST'])
def giveaway_update():
    """Смена ключевого слова / режима без перезапуска чата."""
    data = request.get_json(silent=True) or {}
    if "keyword" in data:
        giveaway["keyword"] = str(data.get("keyword") or "")
    if "accept_any_message" in data:
        giveaway["accept_any_message"] = bool(data.get("accept_any_message"))
    return jsonify({"success": True})


@app.route('/api/reconnect-chat', methods=['POST'])
def reconnect_chat():
    """Сохранить канал и переподключить pytchat, не сбрасывая участников/победителя."""
    global chat_thread, stop_flag
    data = request.get_json(silent=True) or {}
    channel_input = (data.get("channel") or saved_channel.get("channel_id") or "").strip()
    if not channel_input:
        return jsonify({"success": False, "error": "Укажите канал или сохраните ссылку"})
    video_id = get_live_video_id(channel_input)
    if not video_id:
        return jsonify({"success": False, "error": "Не удалось найти активный стрим"})

    saved_channel["channel_id"] = channel_input
    save_channel()

    should_run = bool(giveaway.get("is_active") or giveaway.get("winner"))
    if not should_run:
        giveaway["video_id"] = video_id
        return jsonify({"success": True, "video_id": video_id, "saved_only": True})

    stop_flag = True
    t = chat_thread
    if t and t.is_alive():
        t.join(timeout=5.0)

    stop_flag = False
    giveaway["video_id"] = video_id
    chat_thread = threading.Thread(target=watch_chat, daemon=True)
    chat_thread.start()
    return jsonify({"success": True, "video_id": video_id})


@app.route('/api/reset', methods=['POST'])
def reset():
    global stop_flag
    stop_flag = True
    giveaway["video_id"] = ""
    giveaway["keyword"] = ""
    giveaway["accept_any_message"] = False
    giveaway["participants"] = []
    giveaway["participants_data"] = {}
    giveaway["winner"] = None
    giveaway["winner_avatar"] = None
    giveaway["winner_messages"] = []
    giveaway["winner_picked_at"] = None
    giveaway["winner_first_message_at"] = None
    giveaway["is_active"] = False
    giveaway["is_connected"] = False
    giveaway["countdown"] = 0
    print("🔄 Сброс")
    return jsonify({"success": True})


# === API КАНАЛА ===

@app.route('/api/channel')
def get_channel():
    return jsonify(saved_channel)


@app.route('/api/channel', methods=['POST'])
def update_channel():
    global saved_channel
    saved_channel = request.json
    save_channel()
    return jsonify({"success": True})


# === API НАСТРОЕК ВИДЖЕТА ===

@app.route('/api/widget-settings')
def get_widget_settings():
    return jsonify(widget_settings)


@app.route('/api/widget-settings', methods=['POST'])
def update_widget_settings():
    global widget_settings
    widget_settings = {**default_widget_settings, **request.json}
    save_settings()
    return jsonify({"success": True})


@app.route('/api/fonts')
def get_fonts():
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    fonts = []
    
    if os.path.exists(fonts_dir):
        for file in os.listdir(fonts_dir):
            if file.endswith(('.ttf', '.otf', '.woff', '.woff2')):
                fonts.append(file)
    
    return jsonify(fonts)


@app.route('/api/images')
def get_images():
    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
    images = []
    
    if os.path.exists(images_dir):
        for file in os.listdir(images_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                images.append(file)
    
    return jsonify(images)


# === ЗАПУСК ===

if __name__ == '__main__':
    for folder in ['fonts', 'images']:
        folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"📁 Создана папка: {folder_path}")
    
    print("=" * 50)
    print("🎲 СЕРВЕР РОЗЫГРЫШЕЙ ЗАПУЩЕН")
    print("=" * 50)
    print("📍 Панель управления:   http://localhost:5000")
    print("📍 OBS Dock (компакт):  http://localhost:5000/obs-dock")
    print("📍 Конструктор виджета: http://localhost:5000/constructor")
    print("📍 Виджет для OBS:      http://localhost:5000/widget")
    print("=" * 50)
    print()
    app.run(debug=False, port=5000, threaded=True)