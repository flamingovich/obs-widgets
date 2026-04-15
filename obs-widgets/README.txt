OBS Widgets - единый гайд по запуску
====================================

В этой папке 3 отдельных виджета:
1) giveaway-bot
   - Flask-приложение с giveaway/панелью
   - Локальный URL: http://127.0.0.1:5000

2) random-slot-roulette
   - Node.js сервер для рулетки слотов
   - Локальный URL: http://127.0.0.1:8765

3) wallet-dep-withdraw
   - Python bridge (лайки YouTube) для виджета
   - Локальный URL: http://127.0.0.1:8766
   - По умолчанию порт 8766 (конфликта с roulette нет)


Быстрый запуск (рекомендуется)
------------------------------
1. Запусти файл: start_widgets.bat (из этой корневой папки).
2. В меню выбери:
   [1] Giveaway Bot
   [2] Random Slot Roulette
   [3] Wallet Bridge
   [4] Запустить все сразу
   [0] Выход

Скрипт откроет отдельные окна консоли для выбранных сервисов.
Остановка любого сервиса: Ctrl+C в его окне.


Что за что отвечает
-------------------
giveaway-bot:
- Файлы запуска:
  - giveaway-bot\start_local_server.bat
  - giveaway-bot\giveaway_bot\start_giveaway_bot.bat
- Основной сервер: giveaway-bot\server.py
- Использование:
  - Admin/Panel: http://127.0.0.1:5000

random-slot-roulette:
- Файл запуска: random-slot-roulette\start.bat
- Основной сервер: random-slot-roulette\server.mjs
- Использование:
  - Dock: http://127.0.0.1:8765/dock.html
  - Overlay: http://127.0.0.1:8765/overlay.html

wallet-dep-withdraw:
- Файл запуска: wallet-dep-withdraw\run_bridge.bat
- Основной сервер: wallet-dep-withdraw\likes_bridge.py
- Использование:
  - API: http://127.0.0.1:8766/status?channel=...&goal=...


Требования для запуска
----------------------
Обязательно:
- Windows 10/11
- Python 3.10+ (желательно установлен с галочкой "Add python.exe to PATH")
- Node.js 18+ (для random-slot-roulette)
- Интернет (для некоторых функций, например YouTube likes bridge)

Python-пакеты:
- для wallet-dep-withdraw: pip install -r wallet-dep-withdraw\requirements.txt
- для giveaway-bot (минимум): pip install flask pytchat


Проверка на другом компьютере
-----------------------------
Будет работать на другом ПК, если:
1) Скопировать всю папку obs-widgets целиком.
2) Установить Python и Node.js.
3) Запускать через start_widgets.bat.
4) Разрешить локальные подключения в брандмауэре, если попросит Windows.

Возможные проблемы:
- Порт уже занят другой программой (редко):
  roulette использует 8765, wallet bridge использует 8766.
- Отсутствие Python/Node в PATH.
- Не установлены pip-зависимости.


Если что-то не стартует
-----------------------
1) Проверь версии:
   - python --version
   - node --version
2) Проверь, что запускаешь из этой корневой папки.
3) Запусти нужный подпроект отдельным bat-файлом, чтобы увидеть точную ошибку.
4) Для OBS используй те же URL, что печатаются в консоли.
