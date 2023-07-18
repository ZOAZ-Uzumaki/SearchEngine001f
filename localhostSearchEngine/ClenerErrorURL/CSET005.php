<?php
// Параметри підключення до бази даних
$dbHost = 'localhost';
$dbUsername = 'root';
$dbPassword = '';
$dbName = 'SearchEngine001f';

// Підключення до бази даних
$conn = new mysqli($dbHost, $dbUsername, $dbPassword, $dbName);

// Перевірка наявності помилок при підключенні
if ($conn->connect_error) {
    die("Помилка при підключенні: " . $conn->connect_error);
}

// Отримання даних з таблиці "websites"
$sql = "SELECT id, url FROM websites WHERE url LIKE '%Image URL: %'";
$result = $conn->query($sql);

// Перевірка, чи є дані для обробки
if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        // Видалення "Image URL: " зі строки
        $new_url = str_replace('Image URL: ', '', $row['url']);

        // Оновлення запису в базі даних з виправленим URL
        $update_sql = "UPDATE websites SET url = '$new_url' WHERE id = " . $row['id'];
        $conn->query($update_sql);
    }
}

// Закриття підключення до бази даних
$conn->close();

// Перенаправлення на сторінку HtmlClenerStarter.php з повідомленням про активацію скрипта
header("Location: HtmlClenerStarter.php?message=Script%20activated");
exit();
?>
