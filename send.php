<?php

header('Content-Type: application/json; charset=utf-8');

function fail($code, $msg) {
    http_response_code($code);
    echo json_encode(array('ok' => false, 'error' => $msg), JSON_UNESCAPED_UNICODE);
    exit;
}

// Секреты лежат не в репозитории, а в файле .env (он в .gitignore). Образец — .env.example.
// Сначала ищем .env уровнем выше корня сайта (туда браузер не достанет), потом рядом с send.php.
// Переменные окружения сервера, если заданы, важнее файла.
function load_env() {
    foreach (array(dirname(__DIR__) . '/.env', __DIR__ . '/.env') as $f) {
        if (!is_file($f) || !is_readable($f)) continue;
        $vars = array();
        foreach (file($f, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
            $line = trim($line);
            if ($line === '' || $line[0] === '#' || strpos($line, '=') === false) continue;
            list($k, $v) = explode('=', $line, 2);
            $k = trim($k);
            $v = trim($v);
            // снимаем кавычки: KEY="value" или KEY='value'
            if (strlen($v) >= 2 && ($v[0] === '"' || $v[0] === "'") && substr($v, -1) === $v[0]) {
                $v = substr($v, 1, -1);
            }
            $vars[$k] = $v;
        }
        return $vars;
    }
    return array();
}
$env = load_env();
$envGet = function ($key) use ($env) {
    $v = getenv($key);
    if ($v !== false && $v !== '') return $v;
    return isset($env[$key]) ? $env[$key] : '';
};
$BOT_TOKEN = $envGet('TELEGRAM_BOT_TOKEN');
$CHAT_ID   = $envGet('TELEGRAM_CHAT_ID');
if ($BOT_TOKEN === '' || $CHAT_ID === '') {
    error_log('send.php: не заданы TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID (.env)');
    fail(500, 'Сервер не настроен');
}

// Разрешаем только POST-запросы
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    fail(405, 'Метод не поддерживается');
}

// Простая защита от спама: скрытое поле, которое боты обычно заполняют,
// а обычные пользователи не видят и не трогают
if (!empty($_POST['website'])) {
    // Молча "успешно" отвечаем боту, ничего никуда не отправляя
    echo json_encode(array('ok' => true));
    exit;
}

$post = function ($key) {
    return trim(isset($_POST[$key]) ? (string)$_POST[$key] : '');
};

$name    = $post('name');
$message = $post('message');
$method  = $post('contact_method');
$contact = $post('contact');

// Совместимость со старой версией формы, где было одно поле email
if ($contact === '') {
    $contact = $post('email');
}

if ($name === '') {
    fail(400, 'Укажите имя или название компании');
}
if ($contact === '') {
    fail(400, 'Укажите контакт для связи');
}
if ($message === '') {
    fail(400, 'Опишите задачу');
}

// Согласие на обработку персональных данных — обязательно
if (!isset($_POST['consent']) || $_POST['consent'] === '' || $_POST['consent'] === '0') {
    fail(400, 'Подтвердите согласие на обработку персональных данных');
}

if (mb_strlen($name) > 200 || mb_strlen($contact) > 200 || mb_strlen($message) > 4000) {
    fail(400, 'Слишком длинный текст');
}

// Если способ связи не пришёл (старая форма / бот) — определяем по содержимому
$allowed = array('telegram', 'email', 'phone');
if (!in_array($method, $allowed, true)) {
    if (preg_match('/^@|t\.me\//i', $contact)) {
        $method = 'telegram';
    } elseif (strpos($contact, '@') !== false) {
        $method = 'email';
    } elseif (preg_match('/^[\d\s\+\-\(\)]+$/', $contact)) {
        $method = 'phone';
    } else {
        $method = 'telegram';
    }
}

// Нормализация и проверка контакта по выбранному способу связи
$contactUrl = '';

if ($method === 'telegram') {
    $handle = preg_replace('~^(https?://)?(t\.me/|telegram\.me/)~i', '', $contact);
    $handle = ltrim($handle, '@');
    $handle = preg_replace('~[/?].*$~', '', $handle);
    if (!preg_match('/^[a-zA-Z0-9_]{4,32}$/', $handle)) {
        fail(400, 'Укажите Telegram в формате @username');
    }
    $contact    = '@' . $handle;
    $contactUrl = 'https://t.me/' . $handle;

} elseif ($method === 'email') {
    $contact = preg_replace('/\s+/u', '', $contact);
    if (!filter_var($contact, FILTER_VALIDATE_EMAIL)) {
        fail(400, 'Проверьте адрес электронной почты');
    }
    $contactUrl = 'mailto:' . $contact;

} else { // phone
    $digits = preg_replace('/\D/', '', $contact);
    if (strlen($digits) === 11 && $digits[0] === '8') {
        $digits = '7' . substr($digits, 1);
    }
    if (strlen($digits) < 10 || strlen($digits) > 15) {
        fail(400, 'Укажите телефон в формате +7 (900) 123-45-67');
    }
    if (strlen($digits) === 11 && $digits[0] === '7') {
        $contact = sprintf('+7 (%s) %s-%s-%s',
            substr($digits, 1, 3), substr($digits, 4, 3),
            substr($digits, 7, 2), substr($digits, 9, 2));
    } else {
        $contact = '+' . $digits;
    }
    $contactUrl = 'tel:+' . $digits;
}

$labels = array(
    'telegram' => 'Telegram',
    'email'    => 'Email',
    'phone'    => 'Телефон',
);
$methodLabel = $labels[$method];

function tgEscapeUrl($url) {
    // Внутри ( ) ссылки MarkdownV2 нужно экранировать только ) и \
    return str_replace(array('\\', ')'), array('\\\\', '\\)'), $url);
}

function tgEscape($text) {
    // Экранирование спецсимволов для Telegram MarkdownV2
    return preg_replace('/([_*\[\]()~`>#+\-=|{}.!\\\\])/u', '\\\\$1', $text);
}

$text  = "🔔 *Новая заявка с сайта ONECODEX*\n\n";
$text .= "👤 *Имя или компания:* " . tgEscape($name) . "\n";
$text .= "📨 *Способ связи:* " . tgEscape($methodLabel) . "\n";
$text .= "🔗 *Контакт:* [" . tgEscape($contact) . "](" . tgEscapeUrl($contactUrl) . ")\n";

$page = $post('page');
if ($page === '' && !empty($_SERVER['HTTP_REFERER'])) {
    $page = $_SERVER['HTTP_REFERER'];
}
if ($page !== '' && filter_var($page, FILTER_VALIDATE_URL)) {
    $text .= "🌐 *Страница:* " . tgEscape($page) . "\n";
}

$text .= "\n💬 *Задача:*\n" . tgEscape($message);

$url = "https://api.telegram.org/bot{$BOT_TOKEN}/sendMessage";
$payload = array(
    'chat_id'                  => $CHAT_ID,
    'text'                     => $text,
    'parse_mode'               => 'MarkdownV2',
    'disable_web_page_preview' => 'true',
);

$ch = curl_init($url);
curl_setopt_array($ch, array(
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => http_build_query($payload),
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT        => 10,
    CURLOPT_SSL_VERIFYPEER => true,
));
$response  = curl_exec($ch);
$httpCode  = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curlError = curl_error($ch);
curl_close($ch);

if ($httpCode === 200) {
    echo json_encode(array('ok' => true));
} else {
    // Логируем ошибку на сервере (посмотреть можно в логах хостинга), пользователю — общее сообщение
    error_log('Telegram send error: ' . $httpCode . ' ' . $response . ' ' . $curlError);
    http_response_code(502);
    echo json_encode(array('ok' => false, 'error' => 'Не удалось отправить заявку. Попробуйте позже.'), JSON_UNESCAPED_UNICODE);
}
