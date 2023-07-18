<!DOCTYPE html>
<html>
<head>
    <title>Додавання даних до бази даних</title>
<style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0px;
            padding: 0;
            background-color: #f9f9f9;
            color: #333;
        }

        h1 {
            color: #1a0dab;
            text-align: center;
            margin-bottom: 20px;
        }

        form {
            max-width: 500px;
            margin: 0 auto;
        }

        label {
            display: block;
            margin-bottom: 5px;
        }

        input[type="text"],
        textarea,
        input[type="password"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
            margin-bottom: 10px;
        }

        button[type="submit"],
        .btn-goto {
            background-color: #1a0dab;
            color: #fff;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 4px;
            font-size: 16px;
            transition: background-color 0.2s ease, transform 0.2s ease;
            margin-right: 10px;
        }

        button[type="submit"]:hover,
        .btn-goto:hover {
            background-color: #0d085f;
            transform: scale(1.1);
        }

        .website-type-label {
            display: inline-block;
            margin-bottom: 5px;
        }

        .website-type-select {
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
            margin-bottom: 10px;
        }

        .btn-container {
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
        }

        .database-info {
            max-width: 800px;
            margin: 20px auto;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background-color: #ffffff;
        }

        /* Новий стиль для відображення сайтів у базі даних */
        .website-item {
            margin-bottom: 20px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background-color: #f9f9f9;
            animation: fadeIn 1s ease;
        }

        .website-item p {
            margin: 5px 0;
        }

        .website-item strong {
            color: #1a0dab;
        }

        .website-item img {
            max-width: 100%;
            margin-bottom: 10px;
        }

        /* Загальні стилі для оновленого вигляду сайту */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
            /* Встановлюємо позицію "relative" для контейнера,
               щоб можна було встановити позицію "absolute" для футера
               і він не перекривав контент. */
        }

        header {
            background-color: #1a0dab;
            color: #fff;
            padding: 10px;
            text-align: center;
            position: relative;
            /* Встановлюємо позицію "relative" для хедера,
               щоб можна було встановити позицію "absolute" для футера
               і він не перекривав хедер. */
        }

        header h1 {
            margin: 0;
            color: white;
        }

        nav {
            background-color: #333;
            padding: 10px;
            text-align: center;
        }

        nav a {
            color: #fff;
            text-decoration: none;
            margin: 0 10px;
        }

        nav a:hover {
            text-decoration: underline;
        }

        footer {
            background-color: #1a0dab;
            margin-bottom: -200px;
            color: #fff;
            padding: 10px;
            text-align: center;
            position: absolute;
            bottom: 0;
            width: 100%;
            left: 0;
            /* Встановлюємо позицію "absolute" для футера,
               щоб він розташовувався внизу сторінки. */
        }

        /* Додаткові стилі для анімацій */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>Додавання даних до бази даних</h1>
    </header>
    <div class="container">
        <form method="POST" action="">
            <label for="url">URL:</label>
            <input type="text" name="url" required><br>

            <label for="title">Заголовок:</label>
            <input type="text" name="title" required><br>

            <label for="description">Опис:</label>
            <textarea name="description" rows="4" cols="50" required></textarea><br>

            <label class="website-type-label" for="website_type">Тип сайту:</label>
            <select class="website-type-select" name="website_type">
                <option value="Certified" selected>Certified</option>
                <option value="Darknet">Darknet</option>
            </select><br>

            <label for="image_url">Іконка сайту (image_url):</label>
            <input type="text" name="image_url"><br>

            <label for="image_urls">Список URL зображень (через кому):</label>
            <input type="text" name="image_urls"><br>

            <label for="tags">Список тегів (через кому):</label>
            <input type="text" name="tags"><br>

            <label for="password">Пароль:</label>
            <input type="password" name="password" required><br>

            <button type="submit" name="submit">Додати дані</button>
            <div class="btn-container">
                <button class="btn-goto" onclick="window.location.href = '/DroperFilter003F/FilterBot.php';">Перейти до FilterBot.php</button>
                <button class="btn-goto" onclick="window.location.href = '/DataBaseImporter.php';">Перейти до DataBaseImporter.php</button>
                <button class="btn-goto" onclick="window.location.href = '/RobotSE002F/engine002f.py';">Активувати Python скрипт</button>
            </div>
        </form>

        <?php
        // Підключення до бази даних та перевірка на наявність даних у таблиці
        $dbHost = 'localhost';
        $dbUsername = 'root';
        $dbPassword = '';
        $dbName = 'SearchEngine001f';
        $conn = new mysqli($dbHost, $dbUsername, $dbPassword, $dbName);
        if ($conn->connect_error) {
            die("Помилка підключення до бази даних: " . $conn->connect_error);
        }

        // Перевірка, чи була надіслана форма
        if (isset($_POST['submit'])) {
            $password = $_POST['password'];

            // Перевірка правильності пароля
            if ($password === 'admin') {
                $url = $_POST['url'];
                $title = $_POST['title'];
                $description = $_POST['description'];
                $websiteType = $_POST['website_type'];
                $imageUrl = $_POST['image_url'];

                // Перетворення рядка зі списком зображень на масив
                $imageUrls = explode(',', $_POST['image_urls']);
                $imageUrls = array_map('trim', $imageUrls);
                $imageUrls = array_filter($imageUrls);

                // Перші 20 символів для короткого опису
                $shortDescription = strlen($description) > 20 ? substr($description, 0, 20) . "..." : $description;

                // Внесення даних в базу даних
                $insertQuery = "INSERT INTO websites (url, title, description, short_description, website_type, image_url) VALUES ('$url', '$title', '$description', '$shortDescription', '$websiteType', '$imageUrl')";
                if ($conn->query($insertQuery) === TRUE) {
                    echo "Дані успішно додані до бази даних.";

                    // Перенаправлення користувача після додавання даних
                    header("Location: index.php");
                    exit;
                } else {
                    echo "Помилка під час додавання даних до бази даних: " . $conn->error;
                }
            } else {
                echo '<h2 style="color: red;">Невірний пароль!</h2>';
            }
        }

        // Отримання даних з БД та перевірка наявності запису з айді 1
        $websiteId = 1;
        $selectQuery = "SELECT * FROM websites WHERE id = $websiteId";
        $result = $conn->query($selectQuery);

        // Відображення даних сайту з айді 1
        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            echo '<div class="website-item">';
            echo '<p><strong>URL:</strong> ' . $row['url'] . '</p>';
            echo '<p><strong>Заголовок:</strong> ' . $row['title'] . '</p>';
            echo '<p><strong>Опис:</strong> ' . $row['description'] . '</p>';
            echo '<p><strong>Тип сайту:</strong> ' . $row['website_type'] . '</p>';
            if (!empty($row['image_url'])) {
                echo '<img src="' . $row['image_url'] . '" alt="Іконка сайту">';
            }
            echo '<p><strong>Список URL зображень:</strong> ' . $row['image_urls'] . '</p>';
            echo '<p><strong>Список тегів:</strong> ' . $row['tags'] . '</p>';
            echo '</div>';
        } else {
            echo '<h2 style="color: red;">Сайт з айді 1 не знайдено!</h2>';
        }
        ?>

    </div>
    <footer>
        <p>&copy; <?php echo date("Y"); ?> Всі права захищено.</p>
    </footer>
</body>
</html>
