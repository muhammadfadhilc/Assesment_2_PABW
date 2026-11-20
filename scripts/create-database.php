<?php
require __DIR__.'/../vendor/autoload.php';
Dotenv\Dotenv::createImmutable(dirname(__DIR__))->safeLoad();
$name = $argv[1] ?? $_ENV['DB_DATABASE'] ?? 'recyclehub';
if (!preg_match('/^[a-zA-Z0-9_]+$/', $name)) { throw new RuntimeException('Nama database tidak valid.'); }
$pdo = new PDO('mysql:host='.($_ENV['DB_HOST'] ?? '127.0.0.1').';port='.($_ENV['DB_PORT'] ?? '3306'), $_ENV['DB_USERNAME'] ?? 'root', $_ENV['DB_PASSWORD'] ?? '', [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$pdo->exec('CREATE DATABASE IF NOT EXISTS `'.$name.'` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci');
echo "Database ".$name." siap.\n";
