<!DOCTYPE html>
<html>
<head>
    <title>Очистити URL</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
            padding: 0;
            background-color: #f9f9f9;
        }

        h1 {
            color: #333;
            text-align: center;
        }

        form {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 20px;
        }

        input[type="submit"] {
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            background-color: #007bff;
            color: #fff;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }

        input[type="submit"]:hover {
            background-color: #0056b3;
        }

        /* Стилі для сторінки Html Cleaner Starter */
        .message-box {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            padding: 20px;
            border: 2px solid #007bff;
            border-radius: 10px;
            background-color: #fff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .message-box h2 {
            color: #007bff;
            text-align: center;
        }

        .description {
            margin-top: 40px;
            text-align: center;
            font-size: 18px;
            color: #333;
        }

        .update-warning {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            padding: 10px;
            background-color: #f44336;
            color: #fff;
            text-align: center;
            font-size: 16px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="update-warning">
        Увага! Якщо ви оновите сторінку, запуск очищення URL відбудеться знову.
    </div>

    <h1>Очистити URL</h1>
    <form action="http://localhostsearchengine/ClenerErrorURL/CSET005.php" method="post">
        <input type="submit" value="Очистити URL">
    </form>

    <div class="description">
        <p>Ця програма призначена для очищення URL від зайвої інформації, як-от "Image URL: ", що може з'являтися у деяких URL.</p>
        <p>Для очищення URL натисніть кнопку "Очистити URL". Після виконання програми, ви побачите повідомлення про успішне завершення операції.</p>
    </div>

    <div class="message-box">
        <h2>Повідомлення</h2>
        <script>
            window.onload = function() {
                const urlParams = new URLSearchParams(window.location.search);
                const message = urlParams.get('message');
                if (message) {
                    alert(message);
                }
            };
        </script>
    </div>

    <script>
        // Відображення попередження про оновлення сторінки
        window.onbeforeunload = function() {
            document.querySelector('.update-warning').style.display = 'block';
        };
    </script>
</body>
</html>
