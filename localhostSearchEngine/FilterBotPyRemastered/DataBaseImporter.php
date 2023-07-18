<!DOCTYPE html>
<html>
<head>
    <title>Мій веб-сайт</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }

        .container {
            width: 500px;
            margin: 50px auto;
            padding: 20px;
            border: 1px solid #ccc;
            background-color: #f9f9f9;
        }

        h2 {
            margin-top: 0;
        }

        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: #f3f3f3;
            border: 1px solid #ccc;
            border-radius: 3px;
            overflow: hidden;
        }

        .progress-bar-fill {
            height: 100%;
            background-color: #4caf50;
            transition: width 0.3s ease-in-out;
        }

        .status {
            margin-top: 10px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>Мій веб-сайт</h1>

    <!-- Додайте цей код для кнопки запуску -->
    <button class="console-button" onclick="runProgram()">Запустити програму</button>

    <script>
        function runProgram() {
            // Виконайте тут код для запуску програми
            // Наприклад, викличте PHP-сценарій за допомогою AJAX або відправте запит на сервер
            // для запуску програми і обробки даних з файлу DataBase001T.txt
        }
    </script>
</body>
</html>














<?php
// Параметри підключення до бази даних MySQL
$dbHost = 'localhost';
$dbUsername = 'root';
$dbPassword = '';
$dbName = 'SearchEngine001f';

// Функція для отримання значення іконки сайту (favicon)
function getFavicon($url) {
    $doc = new DOMDocument();
    $doc->strictErrorChecking = false;
    $doc->recover = true;
    $doc->loadHTML(file_get_contents($url));
    $tags = $doc->getElementsByTagName('link');
    foreach ($tags as $tag) {
        if ($tag->getAttribute('rel') == 'icon' || $tag->getAttribute('rel') == 'shortcut icon') {
            return $tag->getAttribute('href');
        }
    }
    return null;
}

// Функція для отримання назви сайту з URL
function getWebsiteTitle($url) {
    $doc = new DOMDocument();
    $doc->strictErrorChecking = false;
    $doc->recover = true;
    $doc->loadHTML(file_get_contents($url));
    $titleTags = $doc->getElementsByTagName('title');
    if ($titleTags->length > 0) {
        return $titleTags[0]->nodeValue;
    }
    return null;
}

// Функція для виправлення записів в таблиці "websites"
function fixWebsiteRecords($conn) {
    // Отримання всіх записів з таблиці "websites"
    $sql = "SELECT * FROM websites";
    $result = $conn->query($sql);
    if ($result->num_rows > 0) {
        while ($row = $result->fetch_assoc()) {
            $website_id = $row['id'];
            $website_url = $row['url'];

            // Виправлення URL сайту
            $fixed_url = fixWebsiteURL($website_url);

            // Виправлення назви сайту (якщо потрібно)
            $website_title = $row['title'];
            if (empty($website_title)) {
                $website_title = getWebsiteTitle($fixed_url);
            }

            // Оновлення запису в таблиці "websites"
            $sql = "UPDATE websites SET url = '$fixed_url', title = '$website_title' WHERE id = '$website_id'";
            if ($conn->query($sql) === TRUE) {
                echo "Запис з ID $website_id в таблиці websites оновлено\n";
            } else {
                echo "Помилка оновлення запису: " . $conn->error . "\n";
            }
        }
    } else {
        echo "Таблиця websites не містить записів\n";
    }
}

// Функція для виправлення URL сайту
function fixWebsiteURL($url) {
    // Видалення "Image URL: " та "URL: " з URL сайту
    $url = str_replace(['Image URL: ', 'URL: '], '', $url);

    return $url;
}

// Функція для перенесення даних з таблиці "websites" до таблиці "images"
function transferData($conn) {
    // Отримання всіх записів з таблиці "websites"
    $sql = "SELECT * FROM websites";
    $result = $conn->query($sql);
    if ($result->num_rows > 0) {
        $image_id = 200; // Початковий ID для таблиці "images"
        while ($row = $result->fetch_assoc()) {
            $website_id = $row['id'];
            $website_url = $row['url'];

            // Перевірка, чи сайт є зображенням
            if (isImageURL($website_url)) {
                // Додавання запису в таблицю "images"
                $sql = "INSERT INTO images (id, website_id, image_url) VALUES ('$image_id', '$website_id', '$website_url')";
                if ($conn->query($sql) === TRUE) {
                    echo "Запис з ID $image_id додано до таблиці images\n";
                } else {
                    echo "Помилка додавання запису: " . $conn->error . "\n";
                }
                $image_id++; // Збільшення ID для наступного запису
            }
        }
    } else {
        echo "Таблиця websites не містить записів\n";
    }
}

// Функція для перевірки, чи URL є зображенням
function isImageURL($url) {
    $imageExtensions = ['jpg', 'jpeg', 'png', 'gif'];
    $extension = strtolower(pathinfo($url, PATHINFO_EXTENSION));
    return in_array($extension, $imageExtensions);
}

// Параметри підключення до бази даних
$conn = new mysqli($dbHost, $dbUsername, $dbPassword, $dbName);
if ($conn->connect_error) {
    die("Помилка підключення до бази даних: " . $conn->connect_error);
}

// Виправлення записів в таблиці "websites"
fixWebsiteRecords($conn);

// Перенесення даних з таблиці "websites" до таблиці "images"
transferData($conn);

$conn->close();
?>
