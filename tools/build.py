#!/usr/bin/env python3
"""Сборка статичного сайта ONECODEX.

Что делает:
  1. Подставляет общую шапку и подвал во все страницы между метками
     <!--header--><!--/header--> и <!--footer--><!--/footer-->.
  2. Собирает карточки кейсов на главной (между <!--cases--> и <!--/cases-->).
  3. Генерирует страницы кейсов case-*.html из списка CASES ниже.

Запуск из корня репозитория:  python3 tools/build.py
После правки шапки, подвала или данных кейсов — просто запустите заново.
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PHONE_HREF = "tel:+79953890192"
PHONE = "+7 995 389-01-92"
TG = "https://t.me/chvanov_ivan"

ICON_PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>'
ICON_TG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M21.9 4.3 18.7 19.4c-.2 1-.9 1.3-1.7.8l-4.8-3.5-2.3 2.2c-.3.3-.5.5-1 .5l.3-4.9 8.9-8c.4-.3-.1-.5-.6-.2L6.5 13.2 1.8 11.7c-1-.3-1-1 .2-1.5L20.6 3c.9-.3 1.6.2 1.3 1.3z"/></svg>'


def header(on_index):
    p = "" if on_index else "index.html"
    return f"""<div class="topline"></div>
<header id="header"><div class="container nav">
  <a class="logo" href="{p or '#top'}" aria-label="ONECODEX — на главную">ONE<i>X</i></a>
  <nav class="navlinks" id="navlinks">
    <a href="{p}#services">Услуги</a><a href="{p}#cases">Работы</a><a href="{p}#process">Процесс</a><a href="{p}#contact">Контакты</a>
  </nav>
  <div class="head-contacts">
    <a class="head-link head-phone" href="{PHONE_HREF}" aria-label="Позвонить {PHONE}">{ICON_PHONE}<span class="ph-text">{PHONE}</span></a>
    <a class="head-link head-tg" href="{TG}" target="_blank" rel="noopener" aria-label="Написать в Telegram">{ICON_TG}<span class="tg-text">Telegram</span></a>
    <a class="cta-small" href="{p}#contact">Передать задачу →</a>
  </div>
  <button class="burger" type="button" aria-label="Меню" aria-controls="navlinks" aria-expanded="false">☰</button>
</div></header>"""


FOOTER = """<footer><div class="container footer"><span>© <span id="year"></span> ONECODEX · Внешний production для агентств</span><a href="mailto:hello@onecodex.ru">hello@onecodex.ru</a><a href="privacy.html">Политика конфиденциальности</a></div></footer>"""


# --------------------------------------------------------------------------
# Кейсы. cat: web — сайты и e-com, ent — enterprise и госсектор, tech — highload, ML, медиа
# --------------------------------------------------------------------------
CASES = [
    dict(
        slug="stilspace", cat="web ent", type="GIS · ДЗЗ · космическая съёмка",
        title="Космическая съёмка Земли", name="StilSpace",
        short="Платформа заказа, каталогизации и обработки спутниковых снимков и отраслевые ГИС-решения.",
        lead="Платформа заказа, каталогизации и обработки данных дистанционного зондирования Земли, а также отраслевые ГИС-решения на их основе.",
        live=("https://stilspace.ru/", "stilspace.ru"),
        shot=("img/case-stilspace.png", "Главный экран портала StilSpace: раздел «Производство»"),
        about=[
            "StilSpace — производитель спутников и оператор данных ДЗЗ. Клиенту нужен был публичный портал, через который заказчики снимков могут искать нужный участок Земли на карте, оценивать доступные материалы съёмки и оформлять заказ, не переписываясь с менеджером по каждому запросу.",
            "Мы спроектировали и собрали WebGIS-платформу: заявки на новую съёмку с разных аппаратов, доступ к архиву российских и иностранных партнёров, автоматическую обработку снимков и визуализацию растровых и векторных данных.",
        ],
        lists=[
            ("Платформа заказа ДЗЗ", [
                "Оперативное формирование заявки на новую съёмку с разных аппаратов",
                "Доступ к архиву данных российских и иностранных партнёров",
                "Каталогизация и хранение снимков в мультивременных слоях",
                "Автоматизированная обработка снимков до требуемого уровня",
                "Визуализация растровых и векторных картографических данных",
                "Комплексные отраслевые решения на основе алгоритмов обработки",
            ]),
            ("ГИС-решения на базе платформы", [
                "Мониторинг объектов критической инфраструктуры",
                "Мониторинг состояния и загрязнения окружающей среды",
                "Мониторинг землепользования",
                "Лесопатологический мониторинг и воспроизводство лесов",
                "Мониторинг недр и водных объектов",
                "Раннее предупреждение и оценка ущерба от ЧС",
            ]),
        ],
        gallery=[("img/works/stilspace-portal.jpg", "Портал: заказ съёмки, доступ к архиву и отраслевые сервисы")],
        stack="Python, TypeScript, Django, FastAPI, SQLAlchemy, PostgreSQL, RabbitMQ, Docker, React, OpenLayers, turf, proj4, MUI, Storybook, Jest, Grafana, Prometheus, Loki",
        tags="React, OpenLayers, FastAPI, PostgreSQL",
    ),
    dict(
        slug="ecosystem", cat="web ent", type="E-commerce экосистема",
        title="Маркетплейс и цифровая экосистема холдинга", name=None,
        short="Связка из полутора десятков систем: маркетплейс, PIM, CRM, WMS, биллинг и мобильные приложения.",
        lead="Развитие e-commerce направления холдинга коммерческой недвижимости: цифровизация торговли и логистики, управление рекламными площадями. Роль — управление созданием связки из полутора десятков систем.",
        live=None,
        shot=("img/works/radiga-desktop.jpg", "Витрина маркетплейса: каталог и персональные рекомендации"),
        about=[
            "Холдингу коммерческой недвижимости нужно было вывести торговлю в онлайн: собственный маркетплейс, агрегатор маркетплейсов, логистика, склады и работа с продавцами.",
            "Мы спроектировали и запустили экосистему, где каждая система отвечает за свою часть процесса, а данные ходят через единую интеграционную шину.",
        ],
        stats=[("15+", "систем в экосистеме"), ("MVP", "агрегатора маркетплейсов"), ("iOS + Android", "приложения для курьеров")],
        lists=[
            ("Системы, вошедшие в экосистему", [
                "Экосистема ТЦ (ERP)", "Marketplace и агрегатор маркетплейсов", "Marketplace Management System",
                "Merchant Administration System", "Billing and Pricing Management", "Product Information Management (PIM)",
                "Digital Asset Management", "Order Management System", "Delivery Service Management",
                "Warehouse Management System", "Integration Data Bus", "CRM, постаматы, реклама",
            ]),
            ("Результат", [
                "Запущен собственный маркетплейс", "Запущен MVP агрегатора маркетплейсов",
                "Готовы MVP мобильных приложений", "Запущена Merchant Administration System",
                "Написан собственный PIM", "Запущена и отлажена CRM",
            ]),
        ],
        gallery=[("img/works/radiga-mobile.jpg", "Мобильное приложение маркетплейса")],
        stack="PHP, Python, Kotlin, Swift, Laravel, Django, Swagger, Postman, 1С, RetailCRM, Диадок, WMS, PIM, Jira, Confluence",
        tags="Laravel, Django, Kotlin, Swift",
    ),
    dict(
        slug="autoparts", cat="web", type="Маркетплейсы · PIM · ценообразование",
        title="Автозапчасти на 8 маркетплейсах", name=None,
        short="Один каталог работает на восьми площадках: карточки из TecDoc, пересчёт цен, синхронные остатки.",
        lead="Один каталог автозапчастей одновременно работает на восьми маркетплейсах и досках объявлений. Система ведёт товарные данные, сама создаёт карточки из TecDoc, пересчитывает цены и раскладывает всё по площадкам без ручной работы.",
        live=("https://www.ozon.ru/seller/ruli-ru-ofitsialnyy-magazin-50269/", "Магазин на Ozon"),
        shot=("img/works/ruli-ozon.jpg", "Витрина магазина автозапчастей на Ozon"),
        about=[
            "Магазину автозапчастей нужно было продавать на Ozon, Wildberries, Яндекс Маркете, AliExpress, Мегамаркете, Магнит Маркете, Avito и Drom, не заводя товары вручную на каждой площадке.",
            "Мы сделали собственную PIM-систему и систему управления ценами. Карточки, категории, цены и остатки приходят на все восемь площадок из одного места.",
        ],
        stats=[("8 площадок", "один магазин на всех одновременно"), ("100+", "параметров в системе управления ценами"), ("TecDoc", "автосоздание карточек из каталога")],
        lists=[
            ("Что сделали", [
                "Собственная система управления товарами (PIM)",
                "Автоматизация создания товаров из каталога TecDoc",
                "Парсеры автозапчастей и интеграция с каталогами поставщиков",
                "Защита фотографий водяными знаками",
                "Управление ценами: 100+ параметров, цены конкурентов, РРЦ, прайсы поставщиков",
                "Единая выгрузка товаров, цен, остатков и заказов на все площадки",
            ]),
        ],
        gallery=[("img/works/ruli-scheme.jpg", "Одна система ведёт каталог и цены, площадки получают данные синхронно")],
        stack="Python, PHP, Django, FastAPI, SQLAlchemy, PostgreSQL, RabbitMQ, Swagger, Grafana, Prometheus, Loki",
        tags="Python, Django, FastAPI, RabbitMQ",
    ),
    dict(
        slug="rushydro", cat="ent", type="Enterprise · BPM · госкорпорация",
        title="АИСУЗ для РусГидро", name=None,
        short="Система управления закупками: 15 модулей, многоступенчатое согласование, ЭЦП и 13 интеграций.",
        lead="Автоматизированная информационная система управления закупками: пятнадцать модулей внутренних бизнес-процессов, сложное согласование, ЭЦП и тринадцать интеграций.",
        live=None,
        shot=("img/works/rushydro-desk.jpg", "АИСУЗ: рабочий стол председателя закупочной комиссии"),
        about=[
            "На каждый модуль — от 150 до 250 страниц технического задания, свой макет и общая дизайн-система.",
            "Стартовый экран собирает в одном месте всё, что нужно участнику закупочного процесса: документы на рассмотрении, статистику, календарь и материалы для работы. Состав виджетов настраивается под роль пользователя.",
        ],
        stats=[("15 модулей", "внутренних бизнес-процессов"), ("7 + 6", "интеграций: системы заказчика и госсистемы"), ("~200 стр.", "ТЗ на каждый модуль")],
        lists=[
            ("Модули системы", [
                "Управление пользователями с ролевой моделью", "Облачное хранилище файлов",
                "Журнал всех операций пользователей", "BPM-модуль: согласование на 200 страниц ТЗ",
                "Электронная цифровая подпись", "Модуль справочников", "Модуль шаблонов и отчётов",
                "Ещё 8 модулей внутренних бизнес-процессов",
            ]),
            ("Архитектура", [
                "Микросервисы на FastAPI и Python, компоненты на Go для высоконагруженных задач",
                "Асинхронный обмен через RabbitMQ, запуск в Docker Compose",
                "Tantor SE 16, SQLAlchemy 2.0 async, Alembic",
                "Файлы в MinIO, полнотекстовый поиск в Elasticsearch",
            ]),
        ],
        gallery=[],
        stack="Python, Go, TypeScript, FastAPI, SQLAlchemy 2.0 async, Alembic, Poetry, Tantor SE 16, MinIO, RabbitMQ, Elasticsearch, Docker Compose, Vue 3, SCSS, Vite, Node.js 18, BEM, FSD",
        tags="FastAPI, Go, Vue 3, Elasticsearch",
    ),
    dict(
        slug="rosstat", cat="ent", type="Государственная отчётность",
        title="Автоматизация сдачи отчётов в Росстат", name=None,
        short="Форма отчёта с онлайн-валидацией, проверка по правилам Росстата и передача по интеграции.",
        lead="Сервис с клиентским и менеджерским функционалом: компания заполняет форму отчёта в удобном интерфейсе, система проверяет её по правилам Росстата ещё до отправки и передаёт данные по интеграции.",
        live=None,
        shot=("img/works/rosstat-api.jpg", "Сверка данных с госсистемой по API: начисления, уплаты, остаток"),
        about=[
            "Отчёт заполняется в привычном по бумажной форме виде, но компактнее: разделы вынесены в оглавление. Онлайн-валидация показывает ошибку сразу и объясняет причину, а не кодом протокола.",
            "Данные подтягиваются из учётной системы или Excel, отчёты обрабатываются пачками. Сверка с госсистемой идёт по API: начисления, уплаты и остаток в одном окне.",
        ],
        lists=[
            ("Что сделали", [
                "Автопроверка отчётов по правилам Росстата и кастомизация правил",
                "Контроль актуальности шаблонов отчётов и самих правил",
                "Форма заполнения отчётов с онлайн-валидацией полей",
                "Интеграция с Росстатом и передача готовых отчётов",
                "Менеджерский контур: клиенты, статусы, сопровождение сдачи",
                "Очереди на RabbitMQ, поиск на Elasticsearch, CI/CD на Jenkins",
            ]),
        ],
        gallery=[
            ("img/works/rosstat-form.jpg", "Форма отчёта: оглавление по разделам и подсказки к полям"),
            ("img/works/rosstat-check.jpg", "Проверка перед отправкой: ошибка подсвечена и объяснена"),
            ("img/works/rosstat-upload.jpg", "Загрузка отчёта из учётной системы или Excel"),
        ],
        stack="C++, Python, JavaScript, STL, Boost, FastAPI, Pandas, BeautifulSoup, Node.js, PostgreSQL, RabbitMQ, Elasticsearch, Loki, Grafana, Jenkins, Docker",
        tags="Python, FastAPI, C++, Elasticsearch",
    ),
    dict(
        slug="crypto", cat="tech", type="Fintech · ML · highload",
        title="Аналитическая платформа по криптовалютам", name=None,
        short="Крупные транзакции, теханализ и тональность публикаций — на этих данных обучаются нейросети.",
        lead="Отслеживание крупных транзакций на рынке криптовалют, сбор статистики технического анализа и анализ тональности публикаций. На этих данных обучаются нейронные сети, которые дают пользователям теханализ, торговые уведомления и рекомендации с минимальными рисками.",
        live=None,
        shot=("img/works/crypto-screener.jpg", "Блокчейн-скринер: подборки кошельков, фильтры и рейтинг"),
        about=[
            "99,9% доступности при потоке около 1000 запросов в минуту. Собственные криптоноды как источник ончейн-данных, проектирование и поддержка базы на несколько терабайт.",
            "Три источника данных: крупные транзакции, рыночная статистика технического анализа и тональность публикаций. Результат отдаётся пользователю как теханализ, уведомления и рекомендации.",
        ],
        stats=[("99,9%", "high availability"), ("1000 rpm", "запросов в минуту"), ("Терабайты", "проектирование и поддержка БД"), ("Свои ноды", "запуск и обслуживание криптонод")],
        lists=[
            ("Функциональность", [
                "Мониторинг крупных транзакций", "Технический анализ и статистика",
                "NLP-анализ тональности публикаций", "Обучение и инференс моделей",
                "Гибкие торговые уведомления", "Торговые боты и интеграции с биржами",
            ]),
        ],
        gallery=[],
        stack="Python, C#, PHP, TensorFlow, scikit-learn, XGBoost, NLTK, Pandas, NumPy, SciPy, Matplotlib, Yii, PostgreSQL, Redis",
        tags="Python, TensorFlow, XGBoost, Redis",
        tall=True,
    ),
    dict(
        slug="videoconf", cat="tech", type="Realtime video · WebRTC",
        title="Система для видеоконференций", name=None,
        short="Вещание 4K / 60 fps на 10 000 одновременных зрителей через WebRTC и eCDN.",
        lead="Платформа видеоконференций и вещания с упором на качество картинки и масштаб аудитории. Доставка потока построена на WebRTC и корпоративной сети доставки контента (eCDN), клиентская часть — на C++/Qt.",
        live=None,
        shot=("img/works/videoconf.jpg", "Тракт вещания: H.264, WebRTC через eCDN, контроль качества по SSIM"),
        about=[
            "Главная задача — доставить 4K-поток большой аудитории без деградации качества. Для этого WebRTC дополнен eCDN, которая распределяет нагрузку внутри корпоративной сети.",
            "Качество контролируется объективной метрикой SSIM на всём тракте кодирования и доставки.",
        ],
        stats=[("SSIM > 0,97", "качество относительно исходника"), ("4K / 60 fps", "вещание в максимальном качестве"), ("10 000", "одновременных пользователей")],
        lists=[
            ("Что решали", [
                "Доставка 4K-потока большой аудитории: WebRTC + eCDN",
                "Кодеки и транспорт: FFmpeg, MPEG-4, H.264, TCP/UDP",
                "Кроссплатформенный клиент на C++/Qt с низкой задержкой",
                "Контроль качества по SSIM на всём тракте",
            ]),
        ],
        gallery=[],
        stack="C++ / C, WebRTC, eCDN, Qt, FFmpeg, TCP / UDP, MPEG-4, H.264",
        tags="C++, Qt, WebRTC, FFmpeg",
    ),
    dict(
        slug="visiontouch", cat="tech", type="Computer vision · интерфейсы",
        title="Nexus VisionTouch", name=None,
        short="Сенсорный экран на любой поверхности и бесконтактное управление жестами.",
        lead="Сенсорный экран на любой плоской поверхности и бесконтактное управление жестами. Проектор и стереокамера превращают витрину, стену или стол в поверхность с неограниченным количеством одновременных касаний.",
        live=None,
        shot=("img/works/visiontouch.jpg", "Камера строит скелет человека по карте глубины: 17 суставов, поза и жесты"),
        about=[
            "Проектор и стереокамера ставятся над произвольной поверхностью. Kinect SDK строит карту глубины сцены, из неё получается матрица точек: касания и жесты. Интерфейс реагирует на них, опираясь на базу 3D-объектов.",
        ],
        stats=[("Мультитач", "неограниченное число касаний"), ("Любая плоскость", "витрина, стена или стол"), ("Жесты", "без оборудования у пользователя")],
        lists=[
            ("Что сделали", [
                "Модули работы с Kinect SDK", "Логика обработки 3D-объектов",
                "Формирование базы объектов сцены", "Логика взаимодействия с матрицей точек",
            ]),
        ],
        gallery=[],
        stack="C++, OpenCV, OpenCL, OpenGL, openFrameworks, Kinect SDK 1.0, PostgreSQL",
        tags="C++, OpenCV, OpenGL, Kinect",
    ),
    dict(
        slug="potolki72", cat="web", type="Сайт-визитка",
        title="potolki72", name=None,
        short="Лендинг для компании натяжных потолков. От приёма заказа до запуска — 5 дней.",
        lead="Сайт-визитка для компании натяжных потолков — от заявки до запущенного лендинга за 5 дней.",
        live=("https://potolki72.tuqo.ru/", "potolki72.tuqo.ru"),
        shot=("img/case-potolki72.png", "Главный экран сайта potolki72"),
        about=[
            "potolki72 работает в Тюмени и Тюменской области и монтирует натяжные потолки любой сложности — от однотонного матового до многоуровневого с подсветкой. Клиенту нужен был простой сайт-визитка: понятное первое предложение, цены, примеры работ и быстрый способ оставить заявку по телефону или в Telegram.",
            "Мы сделали одностраничный лендинг с акцентом на конверсию: конкретные цифры в шапке (срок монтажа, цена за м², гарантия), схема разреза потолка вместо абстрактной иллюстрации и две кнопки связи на первом экране. От приёма заказа до запущенного сайта прошло 5 дней.",
        ],
        stats=[("5 дней", "от заказа до запуска"), ("2 кнопки", "связи на первом экране")],
        lists=[],
        gallery=[],
        stack="HTML, CSS, JavaScript",
        tags="HTML, CSS, JS",
    ),
]


def esc(s):
    return html.escape(s, quote=True)


def tags_html(csv):
    return "".join(f'<span class="tag">{esc(t.strip())}</span>' for t in csv.split(","))


def card(c):
    live = ""
    if c["live"]:
        live = f'<a class="case-live" href="{c["live"][0]}" target="_blank" rel="noopener">{esc(c["live"][1])} ↗</a>'
    return f"""   <article class="case" data-cat="{c['cat']}">
    <div class="case-shot-sm"><img src="img/works/thumb-{c['slug']}.jpg" alt="{esc(c['title'])}" loading="lazy" width="880" height="550"></div>
    <div class="case-body"><span class="case-type">{esc(c['type'])}</span><h3><a href="case-{c['slug']}.html">{esc(c['title'])}</a></h3><p>{esc(c['short'])}</p><div class="tags">{tags_html(c['tags'])}</div>
     <div class="case-foot"><span class="case-more">Подробнее</span>{live}<span class="arrow-ic" aria-hidden="true">→</span></div>
    </div>
   </article>"""


def cases_block():
    cats = [("all", "Все"), ("web", "Сайты и e-com"), ("ent", "Enterprise и госсектор"), ("tech", "Highload, ML, видео")]
    tabs = []
    for key, label in cats:
        n = len(CASES) if key == "all" else sum(key in c["cat"].split() for c in CASES)
        sel = "true" if key == "all" else "false"
        tabs.append(f'<button type="button" class="tab" role="tab" data-filter="{key}" aria-selected="{sel}">{label}<sup>{n}</sup></button>')
    return ('<div class="tabs" role="tablist" aria-label="Фильтр работ">' + "".join(tabs) + "</div>\n"
            '  <div class="case-grid">\n' + "\n".join(card(c) for c in CASES) + "\n  </div>")


HEAD_TMPL = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#09090b">
<link rel="canonical" href="https://onecodex.ru/{file}">
<meta property="og:type" content="article">
<meta property="og:locale" content="ru_RU">
<meta property="og:site_name" content="ONECODEX">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://onecodex.ru/{file}">
<meta property="og:image" content="https://onecodex.ru/{image}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">

<!-- Yandex.Metrika counter -->
<script type="text/javascript">
    (function(m,e,t,r,i,k,a){{
        m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
        m[i].l=1*new Date();
        for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }}}}
        k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
    }})(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=112188634', 'ym');

    ym(112188634, 'init', {{ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true}});
</script>
<noscript><div><img src="https://mc.yandex.ru/watch/112188634" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
<!-- /Yandex.Metrika counter -->

<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<!--header--><!--/header-->
"""


def case_page(c):
    file = f"case-{c['slug']}.html"
    heading = c["title"] + (f" — {c['name']}" if c["name"] else "")
    title = f"{heading} | ONECODEX"
    buttons = []
    if c["live"]:
        buttons.append(f'<a class="btn btn-primary" href="{c["live"][0]}" target="_blank" rel="noopener">Открыть: {esc(c["live"][1])} ↗</a>')
    want = f"Хочу так же, как в проекте «{c['title']}»: "
    better = f"Хочу ещё лучше, чем в проекте «{c['title']}»: "
    buttons.append(f'<a class="btn {"btn-secondary" if c["live"] else "btn-primary"}" href="index.html#contact" data-want="{esc(want)}">Хочу так же <span class="arr">→</span></a>')
    stats = ""
    if c.get("stats"):
        stats = '<div class="stats">' + "".join(f'<div class="stat"><b>{esc(a)}</b><span>{esc(b)}</span></div>' for a, b in c["stats"]) + "</div>"
    shot_style = ' style="max-height:720px;overflow:hidden"' if c.get("tall") else ""
    about = "".join(f"<p>{esc(p)}</p>" for p in c["about"])
    lists = "".join(
        f'<div class="block"><h3>{esc(h)}</h3><ul class="checklist">' + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul></div>"
        for h, items in c["lists"])
    gallery = ""
    if c["gallery"]:
        gallery = '<div class="block"><h3>Как это выглядит</h3><div class="gallery">' + "".join(
            f'<figure><img src="{src}" alt="{esc(cap)}" loading="lazy"><figcaption>{esc(cap)}</figcaption></figure>' for src, cap in c["gallery"]) + "</div></div>"
    live_link = ""
    if c["live"]:
        live_link = f'<a class="link-ext" href="{c["live"][0]}" target="_blank" rel="noopener">Посмотреть вживую: {esc(c["live"][1])} ↗</a>'
    image = c["shot"][0]
    body = f"""<main>

<section class="page-hero">
 <div class="container">
  <a class="back" href="index.html#cases">← Все работы</a>
  <div class="kicker" style="margin-top:22px">{esc(c['type'])}</div>
  <h1>{esc(heading)}</h1>
  <p class="lead">{esc(c['lead'])}</p>
  <div class="buttons">{''.join(buttons)}</div>
  {stats}
  <div class="case-shot"{shot_style}><img src="{c['shot'][0]}" alt="{esc(c['shot'][1])}"></div>
 </div>
</section>

<section class="section-dark">
 <div class="container detail-grid">
  <div>
   <div class="kicker">О проекте</div>
   {about}
   {live_link}
   {lists}
   {gallery}
  </div>
  <div class="meta-list">
   <div class="cap"><strong>Стек</strong><div class="tags">{tags_html(c['stack'])}</div></div>
   <div class="cap"><strong>Нужно похожее?</strong><p>Опишите задачу — за 30 минут разберёмся и предложим решение.</p><div class="buttons" style="margin-top:16px"><a class="btn btn-primary" href="index.html#contact" data-want="{esc(want)}">Хочу так же</a><a class="btn btn-secondary" href="index.html#contact" data-want="{esc(better)}">Хочу ещё лучше</a></div></div>
  </div>
 </div>
</section>
<section class="cta">
 <div class="container"><div class="kicker">Нужен подрядчик</div><h2>Есть похожая задача?</h2><p>Пришлите ссылку, Figma, ТЗ или пару предложений о задаче. Посмотрим объём и скажем, чем можем помочь.</p><div class="buttons"><a class="btn btn-primary btn-lg" href="index.html#contact">Обсудить задачу <span class="arr">→</span></a><a class="btn btn-secondary btn-lg" href="{TG}" target="_blank" rel="noopener">Написать в Telegram ↗</a></div></div>
</section>
</main>
<!--footer--><!--/footer-->
<script src="assets/site.js"></script>
</body>
</html>
"""
    head = HEAD_TMPL.format(title=esc(title), desc=esc(c["lead"][:200]), file=file, image=image)
    (ROOT / file).write_text(head + body, encoding="utf-8")


def fill(text, name, content):
    pat = re.compile(rf"<!--{name}-->.*?<!--/{name}-->", re.S)
    if not pat.search(text):
        return text
    return pat.sub(lambda _: f"<!--{name}-->\n{content}\n<!--/{name}-->", text)


def main():
    for c in CASES:
        case_page(c)
    for path in sorted(ROOT.glob("*.html")):
        t = path.read_text(encoding="utf-8")
        on_index = path.name == "index.html"
        t = fill(t, "header", header(on_index))
        t = fill(t, "footer", FOOTER)
        if on_index:
            t = fill(t, "cases", cases_block())
        path.write_text(t, encoding="utf-8")
    print("ok:", len(CASES), "кейсов")


if __name__ == "__main__":
    main()
