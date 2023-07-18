

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

            // Отримання всіх картинок з URL сайту
            $images = getImagesFromWebsite($website_url);

            // Додавання записів в таблицю "images" для кожної картинки
            foreach ($images as $image) {
                $image_url = $image['url'];

                // Додавання запису в таблицю "images"
                $sql = "INSERT INTO images (id, website_id, image_url) VALUES ('$image_id', '$website_id', '$image_url')";
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

// Функція для отримання всіх картинок з URL сайту
function getImagesFromWebsite($url) {
    $images = [];

    $doc = new DOMDocument();
    $doc->strictErrorChecking = false;
    $doc->recover = true;
    $doc->loadHTML(file_get_contents($url));
    $imgTags = $doc->getElementsByTagName('img');
    foreach ($imgTags as $imgTag) {
        $src = $imgTag->getAttribute('src');

        // Додавання картинки в масив
        $images[] = ['url' => $src];
    }

    return $images;
}

// Параметри підключення до бази даних
$conn = new mysqli($dbHost, $dbUsername, $dbPassword, $dbName);
if ($conn->connect_error) {
    die("Помилка підключення до бази даних: " . $conn->connect_error);
}

// Виклик функції для перенесення даних
transferData($conn);

$conn->close();
?>
