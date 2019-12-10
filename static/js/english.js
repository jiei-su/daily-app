/* ====================
        english
==================== */

//「答えを見る」ボタンクリックで日本語表示
$(function () {
    var jap = $('.japanese')
    $(jap).hide()

    $(document).on('click', '.btn', function() {
        $(this).prev(jap).slideDown();
    });
});