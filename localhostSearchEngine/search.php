<!DOCTYPE html>
<html>
<head>
    <title>Пошукова система</title>
<!--     <style>
        .search-result {
            margin-bottom: 20px;
        }

        .search-result a {
            font-weight: bold;
        }

        .search-result .description {
            margin-top: 5px;
        }
    </style> -->
</head>
<body>
    <h1>Пошукова система</h1>
    <div class="search-form">
        <form method="POST" action="search.php">
            <label for="search-input">Пошук:</label>
            <input type="text" id="search-input" name="searchWord" placeholder="Введіть слово для пошуку" required>
            <button type="submit" name="search">Пошук</button>
        </form>
    
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="load_more.js"></script>
</body>

    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }

        h1 {
            background-color: #1a0dab;
            color: #fff;
            padding: 20px;
            margin: 0;
        }

        .search-form {
            text-align: center;
            margin: 20px;
        }

        .search-form input[type="text"] {
            width: 300px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            transition: border-color 0.3s ease;
        }

        .search-form input[type="text"]:focus {
            outline: none;
            border-color: #1a0dab;
        }

        .search-form button[type="submit"] {
            background-color: #1a0dab;
            color: #fff;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }

        .search-form button[type="submit"]:hover {
            background-color: #0b076c;
        }

        .search-result {
            margin-bottom: 20px;
            padding: 10px;
            background-color: #fff;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        .search-result a {
            font-weight: bold;
            color: #1a0dab;
            text-decoration: none;
        }

        .search-result .description {
            margin-top: 5px;
            color: #555;
        }

        .load-more-button {
            text-align: center;
            margin-top: 20px;
        }

        .load-more-button button {
            background-color: #1a0dab;
            color: #fff;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }

        .load-more-button button:hover {
            background-color: #0b076c;
        }
    </style>

    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }

        h1 {
            background-color: #1a0dab;
            color: #fff;
            padding: 20px;
            margin: 0;
        }

        .tabs {
            margin: 20px;
        }

        .tab-links {
            display: inline-block;
            margin-right: 10px;
        }

        .tab-links li {
            display: inline;
        }

        .tab-links li a {
            color: #1a0dab;
            text-decoration: none;
            padding: 10px;
            border-radius: 5px 5px 0 0;
            background-color: #f2f2f2;
        }

        .tab-links li.active a {
            background-color: #1a0dab;
            color: #fff;
        }

        .tab-content {
            border: 1px solid #1a0dab;
            border-top: none;
            padding: 20px;
            background-color: #f2f2f2;
        }

        .search-form {
            margin-bottom: 20px;
        }

        .search-form input[type="text"] {
            width: 300px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        .search-form button[type="submit"] {
            background-color: #1a0dab;
            color: #fff;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
        }

        .search-result {
            margin-bottom: 20px;
            padding: 10px;
            background-color: #fff;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        .search-result a {
            font-weight: bold;
            color: #1a0dab;
            text-decoration: none;
        }

        .search-result .description {
            margin-top: 5px;
            color: #555;
        }

        .load-more-button {
            text-align: center;
        }

        .load-more-button button {
            background-color: #1a0dab;
            color: #fff;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
        }
        .math-operation {
    background-color: #f2f2f2;
    padding: 5px;
    border-radius: 3px;
    font-weight: bold;
    color: #1a0dab;
    display: inline-block;
}

        .darknet-tag {
            display: inline-block;
            background-color: #000;
            color: #fff;
            padding: 3px 5px;
            border-radius: 3px;
            font-size: 12px;
            margin-top: 5px;
        }




        
    </style>
<?php
$dbHost = 'localhost';
$dbUsername = 'root';
$dbPassword = '';
$dbName = 'SearchEngine001f';

// Підключення до бази даних
$conn = new mysqli($dbHost, $dbUsername, $dbPassword, $dbName);
if ($conn->connect_error) {
    die("Помилка підключення до бази даних: " . $conn->connect_error);
}

if (isset($_POST['search'])) {
    $searchWord = $_POST['searchWord'];

    // Перевірка наявності математичного оператора
    $mathOperators = ['+', '-', '*', '/'];
    $operator = '';
    $number = '';

    foreach ($mathOperators as $mathOperator) {
        if (strpos($searchWord, $mathOperator) !== false) {
            $operator = $mathOperator;
            $parts = explode($mathOperator, $searchWord);
            $number = $parts[0];
            break;
        }
    }

    // Виконання математичної операції, якщо оператор присутній
    $result = '';
    if (!empty($operator) && is_numeric($number)) {
        $operand = $parts[1];
        switch ($operator) {
            case '+':
                $result = $number + $operand;
                break;
            case '-':
                $result = $number - $operand;
                break;
            case '*':
                $result = $number * $operand;
                break;
            case '/':
                $result = $number / $operand;
                break;
        }
    }

    // Виведення результату математичної операції
    if (!empty($result)) {
        echo "<p>Результат обчислення: <span class=\"math-operation\">$searchWord = $result</span></p>";
    }

    // Виконання пошуку сайтів з використанням залишку рядка пошуку
    $searchWord = trim(str_replace([$operator, $operand, ' '], '', $searchWord));

    if (empty($searchWord)) {
        // Якщо поле пошуку порожнє, отримуємо останні додані сайти
        $searchResults = getLastAddedWebsites($conn);
    } else {
        if (is_numeric($searchWord)) {
            // Пошук за ідентифікатором (ID)
            $searchResults = searchWebsitesById($searchWord, $conn);
        } else {
            $searchResults = searchWebsites($searchWord, $conn);
        }
    }

    if (empty($searchResults)) {
        echo "<p>Пошук не дав результатів.</p>";
    } else {
        // Сортування результатів за схожістю до запиту
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

    // Оновлення лічильника пошукових запитів
    $updateQuery = "UPDATE websites SET search_count = search_count + 1";
    $conn->query($updateQuery);

    // Розбиття пошукового слова на токени
    $tokens = explode(' ', $searchWord);
    $tokenQueries = [];

    // Формування окремих запитів для кожного токена
    foreach ($tokens as $token) {
        $token = trim($token);
        $token = mb_strtolower($token, 'UTF-8');
        $tokenQueries[] = "CONCAT_WS(' ', LOWER(url), LOWER(title), LOWER(description)) LIKE '%$token%'";
    }

    // Об'єднання окремих запитів з токенів
    $combinedQuery = implode(" AND ", $tokenQueries);

    // Формування кінцевого запиту
    $finalQuery = "SELECT * FROM websites WHERE $combinedQuery ORDER BY (CASE WHEN LOWER(url) LIKE '%$searchWord%' THEN 1 ELSE 0 END) DESC, (CASE WHEN LOWER(title) LIKE '%$searchWord%' THEN 1 ELSE 0 END) DESC, (CASE WHEN LOWER(description) LIKE '%$searchWord%' THEN 1 ELSE 0 END) DESC";

    // Виконання кінцевого запиту
    $finalResult = $conn->query($finalQuery);
    while ($row = $finalResult->fetch_assoc()) {
        if (!in_array($row, $results)) {
            $results[] = $row;
        }
    }

    return $results;
}



function searchWebsitesById($searchWord, $conn) {
    $results = [];

    $searchWord = $conn->real_escape_string($searchWord);

    // Оновлення лічильника пошукових запитів
    $updateQuery = "UPDATE websites SET search_count = search_count + 1";
    $conn->query($updateQuery);

    // Перетворення введеного значення на ціле число
    $searchId = intval($searchWord);

    // Формування запиту для отримання найближчих айді
    $nearestIdsQuery = "SELECT id FROM websites ORDER BY ABS(id - $searchId) ASC LIMIT 2";
    $nearestIdsResult = $conn->query($nearestIdsQuery);

    // Формування кінцевого запиту за айді
    $finalQuery = "SELECT * FROM websites WHERE id IN (";

    while ($row = $nearestIdsResult->fetch_assoc()) {
        $finalQuery .= $row['id'] . ",";
    }

    $finalQuery = rtrim($finalQuery, ',');
    $finalQuery .= ")";

    // Виконання кінцевого запиту
    $finalResult = $conn->query($finalQuery);
    while ($row = $finalResult->fetch_assoc()) {
        if (!in_array($row, $results)) {
            $results[] = $row;
        }
    }

    return $results;
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
?>





</html>