<?php if (!empty($searchResults)): ?>
    <h3>Результати пошуку за ключовим словом: <?php echo $searchWord; ?></h3>

    <div class="tabs">
        <ul class="tab-links">
            <li><a href="#search-results">Результати пошуку</a></li>
            <li><a href="#image-results">Зображення</a></li>
        </ul>

        <div class="tab-content">
            <div id="search-results" class="tab">
                <?php foreach ($searchResults as $index => $result): ?>
                    <div class="search-result">
                        <a href="<?php echo $result['url']; ?>"><?php echo $result['title']; ?></a> (ID: <?php echo $result['id']; ?>)<br>
                        <span class="description">
                            <?php
                            $description = $result['description'];
                            $shortDescription = strlen($description) > 50 ? substr($description, 0, 100) . "..." : $description;
                            echo $shortDescription;
                            ?>
                        </span><br>
                        <?php if (!empty($result['image_url'])): ?>
                            <img src="<?php echo $result['image_url']; ?>" alt="Картинка сайту" width="30"><br>
                        <?php endif; ?>
                        Силка сайту: <a href="<?php echo $result['url']; ?>"><?php echo $result['url']; ?></a><br>
                        <?php if ($result['website_type'] == 'Onion Darknet'): ?>
                            <span class="darknet-tag">Onion Darknet</span>
                        <?php endif; ?>
                    </div>
                <?php endforeach; ?>

                <?php if (count($searchResults) > 30): ?>
                    <button id="load-more">Показати більше</button>
                <?php endif; ?>
            </div>

            <div id="image-results" class="tab">
                <h3>Зображення, пов'язані з запитом "<?php echo $searchWord; ?>"</h3>
                <?php
                $imageQuery = "SELECT image_url FROM images WHERE website_id IN (SELECT id FROM websites WHERE url LIKE '%$searchWord%')";
                $imageResult = $conn->query($imageQuery);
                ?>

                <?php if ($imageResult && $imageResult->num_rows > 0): ?>
                    <?php while ($row = $imageResult->fetch_assoc()): ?>
                        <?php if (!empty($row['image_url'])): ?>
                            <img src="<?php echo $row['image_url']; ?>" alt="Зображення" width="100">
                        <?php endif; ?>
                    <?php endwhile; ?>
                <?php else: ?>
                    <p>Немає зображень, пов'язаних з запитом "<?php echo $searchWord; ?>"</p>
                <?php endif; ?>
            </div>
        </div>
    </div>


    <script>
        $(document).ready(function () {
            $('.tab-links a').on('click', function (e) {
                var currentAttrValue = $(this).attr('href');
                $('.tab-content ' + currentAttrValue).fadeIn(400).siblings().hide();
                $(this).parent('li').addClass('active').siblings().removeClass('active');
                e.preventDefault();
            });
        });
    </script>
<?php else: ?>
    <p>Немає результатів для ключового слова '<?php echo $searchWord; ?>'.</p>
<?php endif; ?>
