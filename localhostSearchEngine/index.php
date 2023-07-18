<!DOCTYPE html>
<html>
<head>
    <title>Пошукова система</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f2f2f2;
        }

        h1 {
            background-color: #1a0dab;
            color: #fff;
            padding: 20px;
            margin: 0;
            text-align: center;
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
            animation: pulse 1.5s infinite;
        }

        .search-form button[type="submit"]:hover {
            background-color: #0b076c;
            animation: none;
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

        .admin-button {
            background-color: #1a0dab;
            color: #fff;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
            transition: background-color 0.3s ease;
            margin-top: 20px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        footer {
            background-color: #1a0dab;
            padding: 20px;
            text-align: center;
            color: #fff;
            font-size: 14px;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
        }

        @keyframes pulse {
            0% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.1);
            }
            100% {
                transform: scale(1);
            }
        }

        @keyframes slide {
            0% {
                transform: translateY(-50px);
                opacity: 0;
            }
            100% {
                transform: translateY(0);
                opacity: 1;
            }
        }
    </style>
</head>
<body>
    <h1>Пошукова система</h1>
    <div class="search-form">
        <form method="POST" action="search.php">
            <label for="search-input">Пошук:</label>
            <input type="text" id="search-input" name="searchWord" placeholder="Введіть слово для пошуку" required>
            <button type="submit" name="search">Пошук</button>
        </form>
        <p>Використовуйте пошукову систему для знаходження інформації, статей та інших ресурсів.</p>
    </div>

    <div id="search-results-container">
        <?php
        if (isset($_POST['search'])) {
            $searchWord = $_POST['searchWord'];
            $searchResults = searchWebsites($searchWord, $conn);
            include 'search_results.php';
        }
        ?>
    </div>

    <footer>
        &copy; 2023 Пошукова система. Усі права захищені. | <a href="cookie_policy.php" style="color: #fff;">Політика використання кукі</a>
    </footer>

    <button class="admin-button" onclick="location.href='admin.php'">Адмін панель</button>

    <style>
        p {
            font-size: 18px;
            margin: 20px 0;
            animation: slide 1s ease-in-out;
        }
    </style>
</body>
</html>
