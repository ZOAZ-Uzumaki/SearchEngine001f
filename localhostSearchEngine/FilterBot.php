<?php
$dbHost = 'localhost';
$dbUsername = 'root';
$dbPassword = '';
$dbName = 'SearchEngine001f';

$conn = new mysqli($dbHost, $dbUsername, $dbPassword, $dbName);
if ($conn->connect_error) {
    die("Помилка підключення до бази даних: " . $conn->connect_error);
}

if (isset($_POST['search'])) {
    $searchWord = $_POST['searchWord'];

    $searchResults = [];

    if (empty($searchWord)) {
        $searchResults = getLastAddedWebsites($conn);
    } else {
        $searchPath = $_POST['searchPath'];

        if (!empty($searchPath)) {
            $domainCount = getFileCount($searchPath);
            echo "<div><h3>Виконання програми:</h3><textarea rows='10' cols='50' readonly>Знайдено " . $domainCount . " документів для обробки.</textarea></div>";
        }

        if ($searchWord === 'all') {
            $fileList = glob($searchPath . "/*.txt");

            foreach ($fileList as $file) {
                $fileHandle = fopen($file, "r");

                if ($fileHandle) {
                    while (($line = fgets($fileHandle)) !== false) {
                        $data = explode(',', $line);
                        $url = trim($data[0]);
                        $description = trim($data[1]);

                        $parsedUrl = parse_url($url);
                        $parsedDomain = $parsedUrl['host'];

                        $shortDescription = $description;
                        if (empty($shortDescription)) {
                            $shortDescription = $parsedDomain;
                        }

                        $checkSql = "SELECT * FROM websites WHERE url = '$url' OR description = '$description'";
                        $result = $conn->query($checkSql);

                        if ($result->num_rows === 0) {
                            insertData($url, $description, $parsedDomain, $shortDescription, $conn);
                        }
                    }

                    fclose($fileHandle);
                }
            }

            echo "<div><h3>Виконання програми:</h3><textarea rows='10' cols='50' readonly>Програма виконана успішно.</textarea></div>";
        } else {
            $searchWord = $conn->real_escape_string($searchWord);
            $searchResults = searchWebsites($searchWord, $conn);
        }
    }

    if (empty($searchResults)) {
        echo "<div><h3>Виконання програми:</h3><textarea rows='10' cols='50' readonly>Пошук не дав результатів.</textarea></div>";
    } else {
        usort($searchResults, function ($a, $b) use ($searchWord) {
            similar_text($a['url'] . ' ' . $a['title'] . ' ' . $a['description'], $searchWord, $percentA);
            similar_text($b['url'] . ' ' . $b['title'] . ' ' . $b['description'], $searchWord, $percentB);

            return $percentB <=> $percentA;
        });

        include 'search_results.php';
    }
}

function searchWebsites($searchWord, $conn) {
    $results = [];

    $searchWord = $conn->real_escape_string($searchWord);

    $updateQuery = "UPDATE websites SET search_count = search_count + 1";
    $conn->query($updateQuery);

    $tokens = explode(' ', $searchWord);
    $tokenQueries = [];

    foreach ($tokens as $token) {
        $token = trim($token);
        $token = mb_strtolower($token, 'UTF-8');
        $tokenQueries[] = "CONCAT_WS(' ', LOWER(url), LOWER(title), LOWER(description)) LIKE '%$token%'";
    }

    $combinedQuery = implode(" AND ", $tokenQueries);

    $finalQuery = "SELECT * FROM websites WHERE $combinedQuery ORDER BY (CASE WHEN LOWER(url) LIKE '%$searchWord%' THEN 1 ELSE 0 END) DESC, (CASE WHEN LOWER(title) LIKE '%$searchWord%' THEN 1 ELSE 0 END) DESC, (CASE WHEN LOWER(description) LIKE '%$searchWord%' THEN 1 ELSE 0 END) DESC";

    $finalResult = $conn->query($finalQuery);
    while ($row = $finalResult->fetch_assoc()) {
        if (!in_array($row, $results)) {
            $results[] = $row;
        }
    }

    return $results;
}

function getFileCount($searchPath) {
    $fileList = glob($searchPath . "/*.txt");
    return count($fileList);
}

function insertData($url, $description, $domain, $shortDescription, $conn) {
    $sql = "INSERT INTO websites (url, description, domain, short_description) VALUES ('$url', '$description', '$domain', '$shortDescription')";

    if ($conn->query($sql) === true) {
        echo "<div><h3>Виконання програми:</h3><textarea rows='10' cols='50' readonly>Дані успішно додано до бази даних.</textarea></div>";
    } else {
        echo "<div><h3>Виконання програми:</h3><textarea rows='10' cols='50' readonly>Помилка: " . $sql . "<br>" . $conn->error . "</textarea></div>";
    }
}

function getLastAddedWebsites($conn) {
    $results = [];

    $lastAddedQuery = "SELECT * FROM websites ORDER BY date_added DESC LIMIT 10";
    $lastAddedResult = $conn->query($lastAddedQuery);
    while ($row = $lastAddedResult->fetch_assoc()) {
        $results[] = $row;
    }

    return $results;
}

$conn->close();
?>


<!DOCTYPE html>
<html>
<head>
    <title>Search Engine</title>
    <style>
        body {
            font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
            background-color: #000;
            color: #0f0;
            overflow: hidden;
        }

        h1 {
            margin: 0;
            padding: 10px;
            font-size: 36px;
            text-align: center;
            animation: blink 1s infinite;
        }

        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0; }
            100% { opacity: 1; }
        }

        form {
            margin: 20px;
            padding: 10px;
            text-align: center;
            animation: slideIn 1s;
        }

        @keyframes slideIn {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(0); }
        }

        label {
            font-size: 18px;
        }

        input[type="text"] {
            padding: 5px;
            margin: 5px;
            font-size: 16px;
        }

        input[type="submit"] {
            padding: 5px 20px;
            margin: 10px;
            font-size: 18px;
            background-color: #060;
            border: none;
            color: #000;
            cursor: pointer;
            animation: blink 1s infinite;
        }

        input[type="submit"]:hover {
            background-color: #090;
        }

        textarea {
            width: 100%;
            height: 200px;
            background-color: #000;
            color: #0f0;
            border: none;
            font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
            resize: none;
            animation: blink 1s infinite;
        }

        .description {
            margin: 20px;
            padding: 10px;
            text-align: center;
            animation: slideIn 1s;
        }

        .description h3 {
            font-size: 24px;
            margin-bottom: 10px;
        }

        .description p {
            margin: 0;
            padding-bottom: 10px;
            line-height: 1.5;
        }

        .command-info {
            margin-bottom: 10px;
            font-size: 14px;
        }

        .version {
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 12px;
            color: #0f0;
        }
    </style>
</head>
<body>
    <h1>Search Engine</h1>
    <form method="post" action="">
        <label for="searchWord">Пошук:</label>
        <input type="text" name="searchWord" id="searchWord">
        <br>
        <span class="command-info">(Введіть "all" для пошуку всіх документів)</span>
        <br><br>
        <label for="searchPath">Шлях для пошуку:</label>
        <input type="text" name="searchPath" id="searchPath">
        <br>
        <span class="command-info">(Введіть шлях до теки з .txt файлами)</span>
        <br><br>
        <input type="submit" name="search" value="Пошук">
        <input type="submit" name="checkDomainCount" value="Перевірити кількість документів">
    </form>

    <div class="description">
        <h3>Опис:</h3>
        <p>Ця сторінка є частиною модуля "DroperFilter003F" і використовується для сортування та збереження даних, зібраних від інтернет павука.</p>
    </div>
    <div>
        <h3>Виконання програми:</h3>
        <textarea rows="10" cols="50" readonly><?php echo isset($result) ? $result : ""; ?></textarea>
    </div>
    <div class="version">
        Версія програми: 1.0
    </div>
</body>
</html>
