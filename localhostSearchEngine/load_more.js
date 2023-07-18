$(document).ready(function () {
    var resultsPerPage = 30;
    var currentPage = 1;
    var totalResults = <?php echo count($searchResults); ?>;
    var totalPages = Math.ceil(totalResults / resultsPerPage);

    if (totalPages > 1) {
        $('#load-more').show();
    }

    $('#load-more').click(function () {
        currentPage++;
        var endIndex = currentPage * resultsPerPage;

        $('.search-result').slice(0, endIndex).show();

        if (currentPage >= totalPages) {
            $('#load-more').hide();
        }
    });
});
