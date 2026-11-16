<?php
/**
 * Приём заявки с формы и отправка её в Telegram.
 *
 * Что изменилось по сравнению с прежней версией:
 *  - токен бота и chat_id вынесены в файл выше public_html (раньше лежали
 *    в этом файле и уезжали с каждой копией исходников);
 *  - добавлен лимит на число заявок с одного IP;
 *  - добавлена проверка Origin/Referer — чужой сайт не может слать заявки
 *    в ваш чат от имени посетителя;
 *  - добавлена проверка времени заполнения (боты отправляют мгновенно);
 *  - тексты ошибок больше не раскрывают внутреннее устройство.
 *
 * Код совместим с PHP 5.6 и 8.x. На хостинге стоит переключить сайт
 * на PHP 8.1+: 5.6 не получает обновлений безопасности с 2018 года.
 */

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

// ─── Конфигурация ───────────────────────────────────────────────────────────
$configPath = dirname(__DIR__) . '/onecodex-config.php';
if (!is_readable($configPath)) {
    error_log('ONECODEX: не найден onecodex-config.php по пути ' . $configPath);
    http_response_code(500);
    echo json_encode(array('ok' => false, 'error' => 'Форма временно недоступна. Напишите нам в Telegram.'), JSON_UNESCAPED_UNICODE);
    exit;
}
$CFG = require $configPath;

function fail($code, $msg) {
    http_response_code($code);
    echo json_encode(array('ok' => false, 'error' => $msg), JSON_UNESCAPED_UNICODE);
    exit;
}

// ─── Только POST ────────────────────────────────────────────────────────────
if (!isset($_SERVER['REQUEST_METHOD']) || $_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Allow: POST');
    fail(405, 'Метод не поддерживается');
}

// ─── Заявка должна приходить с нашего же сайта ──────────────────────────────
$origin = '';
if (!empty($_SERVER['HTTP_ORIGIN'])) {
    $origin = $_SERVER['HTTP_ORIGIN'];
} elseif (!empty($_SERVER['HTTP_REFERER'])) {
    $p = parse_url($_SERVER['HTTP_REFERER']);
    if (!empty($p['scheme']) && !empty($p['host'])) {
        $origin = $p['scheme'] . '://' . $p['host'];
    }
}
if ($origin !== '' && !in_array($origin, $CFG['allowed_origins'], true)) {
    fail(403, 'Запрос отклонён');
}

// ─── Honeypot: скрытое поле, которое видят только боты ──────────────────────
if (!empty($_POST['website'])) {
    // Молча отвечаем «успешно», ничего никуда не отправляя
    echo json_encode(array('ok' => true));
    exit;
}

$post = function ($key) {
    return trim(isset($_POST[$key]) ? (string)$_POST[$key] : '');
};

// ─── Ловушка на скорость: человек не заполняет форму за секунду ─────────────
$ts = (int)$post('ts');
if ($ts > 0) {
    $elapsed = time() - (int)($ts / 1000);
    if ($elapsed >= 0 && $elapsed < (int)$CFG['min_fill_seconds']) {
        echo json_encode(array('ok' => true)); // так же молча
        exit;
    }
}

// ─── Лимит заявок с одного IP ───────────────────────────────────────────────
function client_ip() {
    return isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '0.0.0.0';
}
function rate_limited($bucket, $limit, $window) {
    $dir = sys_get_temp_dir() . '/onecodex-rl';
    if (!is_dir($dir)) { @mkdir($dir, 0700, true); }
    if (!is_dir($dir)) { return false; } // не смогли — не блокируем живых людей
    $file = $dir . '/' . $bucket . '-' . sha1(client_ip()) . '.txt';
    $now  = time();
    $hits = array();
    if (is_readable($file)) {
        foreach (explode("\n", (string)@file_get_contents($file)) as $line) {
            $t = (int)trim($line);
            if ($t > 0 && $now - $t < $window) { $hits[] = $t; }
        }
    }
    if (count($hits) >= $limit) { return true; }
    $hits[] = $now;
    @file_put_contents($file, implode("\n", $hits), LOCK_EX);
    // Изредка подчищаем старые файлы, чтобы каталог не разрастался
    if (mt_rand(1, 50) === 1) {
        foreach ((array)glob($dir . '/*.txt') as $f) {
            if (@filemtime($f) < $now - $window * 24) { @unlink($f); }
        }
    }
    return false;
}
// Грубый лимит на число обращений вообще — против простого флуда.
// Ошибки заполнения формы сюда попадают, поэтому запас большой.
if (rate_limited('req', (int)$CFG['rate_limit'] * 6, (int)$CFG['rate_window'])) {
    fail(429, 'Слишком много запросов. Попробуйте позже или напишите нам в Telegram.');
}

// ─── Данные формы ───────────────────────────────────────────────────────────
$name    = $post('name');
$message = $post('message');
$method  = $post('contact_method');
$contact = $post('contact');

// Совместимость со старой версией формы, где было одно поле email
if ($contact === '') { $contact = $post('email'); }

// Управляющие символы в Telegram не нужны и ломают разметку
$strip = function ($s) {
    return preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $s);
};
$name = $strip($name); $message = $strip($message); $contact = $strip($contact);

if ($name === '')    { fail(400, 'Укажите имя или название компании'); }
if ($contact === '') { fail(400, 'Укажите контакт для связи'); }
if ($message === '') { fail(400, 'Опишите задачу'); }

if (mb_strlen($name) > 200 || mb_strlen($contact) > 200 || mb_strlen($message) > 4000) {
    fail(400, 'Слишком длинный текст');
}

// Если способ связи не пришёл (старая форма / бот) — определяем по содержимому
$allowed = array('telegram', 'email', 'phone');
if (!in_array($method, $allowed, true)) {
    if (preg_match('/^@|t\.me\//i', $contact))            { $method = 'telegram'; }
    elseif (strpos($contact, '@') !== false)              { $method = 'email'; }
    elseif (preg_match('/^[\d\s\+\-\(\)]+$/', $contact))  { $method = 'phone'; }
    else                                                  { $method = 'telegram'; }
}

// ─── Согласие на обработку персональных данных — обязательно ────────────────
if (!isset($_POST['consent']) || $_POST['consent'] === '' || $_POST['consent'] === '0') {
    fail(400, 'Подтвердите согласие на обработку персональных данных');
}

// ─── Нормализация и проверка контакта ───────────────────────────────────────
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
    if (!filter_var($contact, FILTER_VALIDATE_EMAIL) || mb_strlen($contact) > 254) {
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

$labels = array('telegram' => 'Telegram', 'email' => 'Email', 'phone' => 'Телефон');
$methodLabel = $labels[$method];

// ─── Сборка сообщения для Telegram ──────────────────────────────────────────
function tgEscapeUrl($url) {
    // Внутри ( ) ссылки MarkdownV2 экранируются только ) и \
    return str_replace(array('\\', ')'), array('\\\\', '\\)'), $url);
}
function tgEscape($text) {
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
// Показываем адрес страницы, только если он с нашего же сайта
if ($page !== '' && filter_var($page, FILTER_VALIDATE_URL)) {
    $ph = parse_url($page);
    $pOrigin = (!empty($ph['scheme']) && !empty($ph['host'])) ? $ph['scheme'] . '://' . $ph['host'] : '';
    if (in_array($pOrigin, $CFG['allowed_origins'], true)) {
        $text .= "🌐 *Страница:* " . tgEscape($page) . "\n";
    }
}

$text .= "\n💬 *Задача:*\n" . tgEscape($message);

// ─── Строгий лимит: сколько заявок реально уходит в чат ─────────────────────
// Проверяем здесь, а не в начале: тогда опечатки в форме не расходуют лимит
// живого человека, а флудить чат всё равно не получится.
if (rate_limited('send', (int)$CFG['rate_limit'], (int)$CFG['rate_window'])) {
    fail(429, 'Слишком много заявок за короткое время. Попробуйте позже или напишите нам в Telegram.');
}

// ─── Отправка ───────────────────────────────────────────────────────────────
$url = 'https://api.telegram.org/bot' . $CFG['bot_token'] . '/sendMessage';
$payload = array(
    'chat_id'                  => $CFG['chat_id'],
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
    CURLOPT_CONNECTTIMEOUT => 5,
    CURLOPT_SSL_VERIFYPEER => true,
    CURLOPT_SSL_VERIFYHOST => 2,
));
$response  = curl_exec($ch);
$httpCode  = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curlError = curl_error($ch);
curl_close($ch);

if ($httpCode === 200) {
    echo json_encode(array('ok' => true));
} else {
    // Подробности — только в лог хостинга, пользователю общее сообщение
    error_log('ONECODEX Telegram send error: ' . $httpCode . ' ' . $response . ' ' . $curlError);
    http_response_code(502);
    echo json_encode(array('ok' => false, 'error' => 'Не удалось отправить заявку. Попробуйте позже.'), JSON_UNESCAPED_UNICODE);
}