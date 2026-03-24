<?php

$sharePath = $_GET['share_path'] ?? '';

if (!is_string($sharePath) || !preg_match('#^/(s|share/posts)/[A-Za-z0-9_-]+$#', $sharePath)) {
    http_response_code(400);
    header('Content-Type: text/plain; charset=utf-8');
    echo 'Invalid share path.';
    exit;
}

$apiBase = getenv('CRAFTYXHUB_SHARE_PROXY_BASE') ?: 'https://api.craftyxhub.com';
$upstreamUrl = rtrim($apiBase, '/') . $sharePath;
$method = strtoupper($_SERVER['REQUEST_METHOD'] ?? 'GET');

$curl = curl_init($upstreamUrl);
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
curl_setopt($curl, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curl, CURLOPT_HEADER, true);
curl_setopt($curl, CURLOPT_USERAGENT, $_SERVER['HTTP_USER_AGENT'] ?? 'CraftyXHubShareProxy/1.0');

if ($method === 'HEAD') {
    curl_setopt($curl, CURLOPT_NOBODY, true);
    curl_setopt($curl, CURLOPT_CUSTOMREQUEST, 'HEAD');
}

$response = curl_exec($curl);

if ($response === false) {
    http_response_code(502);
    header('Content-Type: text/plain; charset=utf-8');
    echo 'Unable to fetch share page.';
    curl_close($curl);
    exit;
}

$statusCode = curl_getinfo($curl, CURLINFO_RESPONSE_CODE) ?: 200;
$headerSize = curl_getinfo($curl, CURLINFO_HEADER_SIZE) ?: 0;
$rawHeaders = substr($response, 0, $headerSize);
$body = substr($response, $headerSize);

curl_close($curl);

http_response_code($statusCode);

$forwardableHeaders = [
    'content-type',
    'cache-control',
    'x-robots-tag',
];

foreach (preg_split("/\r\n|\n|\r/", trim($rawHeaders)) as $headerLine) {
    if (!str_contains($headerLine, ':')) {
        continue;
    }

    [$name, $value] = array_map('trim', explode(':', $headerLine, 2));
    if (in_array(strtolower($name), $forwardableHeaders, true)) {
        header($name . ': ' . $value, true);
    }
}

if ($method !== 'HEAD') {
    echo $body;
}
