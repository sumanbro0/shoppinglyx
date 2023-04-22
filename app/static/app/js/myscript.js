$('#slider1, #slider2, #slider3').owlCarousel({
    loop: true,
    margin: 20,
    responsiveClass: true,
    responsive: {
        0: {
            items: 1,
            nav: false,
            autoplay: true,
        },
        600: {
            items: 3,
            nav: true,
            autoplay: true,
        },
        1000: {
            items: 5,
            nav: true,
            loop: true,
            autoplay: true,
        }
    }
})

$('.plus-cart').click(function () {
    var id = $(this).attr("pid").toString();
    var elm = this.parentNode.children[2];
    $.ajax({
        type: "GET",
        url: "/pluscart",
        data: {
            prod_id: id,
        },
        success: function (data) {
            elm.innerText = data.quantity;
            $('#amount').text(data.amount);
            $('#totalamount').text(data.total_amount);

        },

    })
})
$('.minus-cart').click(function () {
    var id = $(this).attr("pid").toString();
    var elm = this.parentNode.children[2];
    $.ajax({
        type: "GET",
        url: "/minuscart",
        data: {
            prod_id: id,
        },
        success: function (data) {
            elm.innerText = data.quantity;
            $('#amount').text(data.amount);
            $('#totalamount').text(data.total_amount);
        },

    })
})
$('.remove-cart').click(function () {
    var id = $(this).attr("pid").toString();
    var elm = this

    $.ajax({
        type: "GET",
        url: "/removecart",
        data: {
            prod_id: id,
        },
        success: function (data) {
            $('#amount').text(data.amount);
            $('#totalamount').text(data.total_amount);
            elm.parentNode.parentNode.parentNode.parentNode.remove();
        },

    })
})
