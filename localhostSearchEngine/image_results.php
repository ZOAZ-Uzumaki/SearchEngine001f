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

$imageQuery = "SELECT image_url FROM images WHERE website_id IN (SELECT id FROM websites WHERE url LIKE '%$searchWord%')";
$imageResult = $conn->query($imageQuery);
?>

<?php if ($imageResult && $imageResult->num_rows > 0): ?>
    <h3>Зображення, пов'язані з запитом "<?php echo $searchWord; ?>"</h3>

    <?php
    $imageUrls = [];
    while ($row = $imageResult->fetch_assoc()) {
        if (!empty($row['image_url'])) {
            $imageUrls[] = $row['image_url'];
        }
    }

    shuffle($imageUrls);
    $imageUrls = array_slice($imageUrls, 0, 5);
    ?>

    <?php foreach ($imageUrls as $imageUrl): ?>
        <img src="<?php echo $imageUrl; ?>" alt="Зображення" width="100">
    <?php endforeach; ?>

<?php else: ?>  
    <p>Немає зображень, пов'язаних з запитом "<?php echo $searchWord; ?>"</p>
<?php endif; ?>

<?php
$conn->close();
?>



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
    </style>
