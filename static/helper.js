"use strict";

let COUNTER = 0;
let CUISINE_COUNT = 0;
let HIDDEN_INPUTS;


// To initialize tooltips and define HIDDEN_INPUTS

$(document).ready(function() {
    $("body").tooltip({ selector: '[data-toggle=tooltip]' });
    HIDDEN_INPUTS = $("[type=hidden]");
});



// carousel (from Tom Michew)

$('#carouselExample').on('slide.bs.carousel', function (e) {

    var $e = $(e.relatedTarget);
    var idx = $e.index();
    var itemsPerSlide = 4;
    var totalItems = $('.carousel-item').length;
    
    if (idx >= totalItems-(itemsPerSlide-1)) {
        var it = itemsPerSlide - (totalItems - idx);
        for (var i=0; i<it; i++) {
            // append slides to end
            if (e.direction=="left") {
                $('.carousel-item').eq(i).appendTo('.carousel-inner');
            }
            else {
                $('.carousel-item').eq(0).appendTo('.carousel-inner');
            }
        }
    }
});


// Behavior of cuisine input
console.log("this is CUISINE_COUNT before selecting: " + CUISINE_COUNT);
$(".cuisine").on("click", function() {
    CUISINE_COUNT += 1;
    $(this).removeClass("not");
    console.log("this is CUISINE_COUNT after selecting: " + CUISINE_COUNT);
    if (CUISINE_COUNT >= 3) {
        $(".not").attr("disabled", "");
        console.log("this is CUISINE_COUNT after disabling: " + CUISINE_COUNT);
    }
});




// Behavior of recipe-select buttons 

let button = $(".recipe-select");
console.log("this is the counter before clicking: " + COUNTER);
let dataObj = {
    "1": "",
    "2": "",
    "3": "",
    "4": "",
    "5": ""
};

function changeButton(evt) {
if ($(this).html() === "Select") {
    COUNTER += 1;
    console.log("this is the counter after saving: " + COUNTER);
    $(this).removeClass("unsaved");
    $(this).addClass("saved");
    let buttonData = $(this).data();    // a dict

    // loop over HIDDEN_INPUTS
    // if .attr("value","") is true: add buttonData and break
    // else: continue 
    // for (let input in HIDDEN_INPUTS) {
    //     if ()
    // }

    for (let day in dataObj) {
        if (dataObj[day] === "") {
            dataObj[day] = JSON.stringify(buttonData);
            $(this).html("Saved for Day " + day);
            $(HIDDEN_INPUTS[day-1]).attr("value", dataObj[day]);
            break;
            }
        }
    } 

else {
    let day = $(this).html()[$(this).html().length - 1]-1;
    $(HIDDEN_INPUTS[day]).attr("value", "");
    dataObj[day+1] = "";
    $(this).html("Select");
    $(this).removeClass("saved");
    $(this).addClass("unsaved");
    COUNTER -= 1;
    console.log("this is the counter after unsaving: " + COUNTER);
    }

if (5-COUNTER === 1) {
    $(".results-msg").html("Select " + (5-COUNTER) + " more recipe");
} else {
    $(".results-msg").html("Select " + (5-COUNTER) + " more recipes");
}

if (COUNTER === 5) {
    $("#create").css("visibility", "visible");
    $(".unsaved").css("visibility", "hidden");
    $(".results-msg").css("visibility", "hidden");
    }

else {
    $(".unsaved").css("visibility", "visible");
    $("#create").css("visibility", "hidden");
    $(".results-msg").css("visibility", "visible");
    }
}

button.on('click',changeButton);



// CHARTS


let options = {
    legend: {
        display: false
    },
    // events: []
};


function makeNutriDict(id, nutrient) {
    let button = $("#"+id);
    let percentOfDailyNeeds;

    if (nutrient === "Fat") {
        percentOfDailyNeeds = button.data("fat");
    }
    else if (nutrient === "Carbs") {
        percentOfDailyNeeds = button.data("carbs");
    }
    if (nutrient === "Protein") {
        percentOfDailyNeeds = button.data("protein");
    }

    let data_dict = {
                "labels": [
                    nutrient,
                    "remainder"
                ],
                "datasets": [
                    {
                        "data": [percentOfDailyNeeds, 100-percentOfDailyNeeds],
                        "backgroundColor": [
                            "#4A7E13",
                            "gray"
                        ],
                        "hoverBackgroundColor": [
                            "#4A7E13",
                            "gray"
                        ]
                    }]
            };

    return data_dict;
}


function makeFatChart(data, chart) {
      options["title"] = {
            display: true,
            text: 'Fat'
        };
      let fatChart = new Chart(chart, {
                                              type: 'doughnut',
                                              data: data,
                                              options: options
                                            });
    }

function makeCarbsChart(data, chart) {
      options["title"] = {
            display: true,
            text: 'Carbs'
        };
      let carbsChart = new Chart(chart, {
                                              type: 'doughnut',
                                              data: data,
                                              options: options
                                            });
    }

function makeProteinChart(data, chart) {
      options["title"] = {
            display: true,
            text: 'Protein'
        };
      let proteinChart = new Chart(chart, {
                                              type: 'doughnut',
                                              data: data,
                                              options: options
                                            });
    }


function makeCharts() {
    let id = this.id;
    let fat = makeNutriDict(id, "Fat");
    let carbs = makeNutriDict(id, "Carbs");
    let protein = makeNutriDict(id, "Protein");

    let ctx_donut1 = $("#donutChart1").get(0).getContext("2d");
    let ctx_donut2 = $("#donutChart2").get(0).getContext("2d");
    let ctx_donut3 = $("#donutChart3").get(0).getContext("2d");

    makeFatChart(fat, ctx_donut1);
    makeCarbsChart(carbs, ctx_donut2);
    makeProteinChart(protein, ctx_donut3);

    $(".hide").css("visibility", "visible");
}

// $(".nutrition").on('click', makeCharts);




// To initialize popovers

// $(function () {
//   $('[data-toggle="popover"]').popover({
//     container: 'body'
//   });
// });

// $("[data-toggle=popover]").popover({
//     container: 'body',
//     html: true, 
//     content: function() {
//           return $('#popover-content').html();
//         }
// });


$('[data-toggle="popover"]').popover({
  html: true,
  content: '<canvas id="donutChart1" width="25" height="25"></canvas><canvas id="donutChart2" width="25" height="25"></canvas><canvas id="donutChart3" width="25" height="25"></canvas>',
}).on('shown.bs.popover', makeCharts);


$('.popover-dismiss').popover({
  trigger: 'focus'
});
