/* ====================
        common
==================== */

// カレントURLを取得し、ナビゲーションをアクティブにする
$(function(){
    $('.footerList a').each(function(){
      var $href = $(this).attr('href');

      if(location.href.match($href)) {
        $(this).parent().addClass('current-href');
      } else {
        $(this).parent().removeClass('current-href');
      }
    });
});