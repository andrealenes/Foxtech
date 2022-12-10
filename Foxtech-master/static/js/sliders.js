'use strict';

const sliders = document.querySelectorAll(".glider");

    for (let i = 0; i <= sliders.length; i++) {
        new Glider(sliders[i], { 
            slidesToScroll: 1,
            slidesToShow: 1,
            draggable: true,
            arrows: {
                prev: (i == 0) ? '.glider-prev' : `.glider-prev${i}`,
                next: (i == 0) ? '.glider-next' : `.glider-next${i}`
            },
            responsive: [
                {
                    breakpoint: 600,
                    settings: {
                        slidesToScroll: 1,
                        slidesToShow: 2,
                    }
                },
                {
                    breakpoint: 800,
                    settings: {
                        slidesToScroll: 1,
                        slidesToShow: 3,
                    }
                },
                {
                    breakpoint: 1000,
                    settings: {
                        slidesToScroll: 1,
                        slidesToShow: 4,
                    }
                },
                {
                    breakpoint: 1200,
                    settings: {
                        slidesToScroll: 1,
                        slidesToShow: 5,
                    }
                },
                {
                    breakpoint: 1600,
                    settings: {
                        slidesToScroll: 1,
                        slidesToShow: 6,
                    }
                },
                {
                    breakpoint: 1800,
                    settings: {
                        slidesToScroll: 1,
                        slidesToShow: 7,
                    }
                }
            ]
        });
    }