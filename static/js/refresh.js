$('.select').click(function () {
    setTimeout(function () {
        location.reload(true);
    }, 2000);
});

$('.redirect').click(function () {
    setTimeout(function () {
        window.location.replace("/appointments");
    }, 2000);
});

(function ($) {
    function floatLabel(inputType) {
        $(inputType).each(function () {
            var $this = $(this);
            // on focus add cladd active to label
            $this.focus(function () {
                $this.next().addClass("active");
            });
            //on blur check field and remove class if needed
            $this.blur(function () {
                if ($this.val() === '' || $this.val() === 'blank') {
                    $this.next().removeClass();
                }
            });
        });
    }
    // just add a class of "floatLabel to the input field!"
    floatLabel(".floatLabel");
})(jQuery);