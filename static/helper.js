"use strict";

let COUNTER = 0;
let HIDDEN_INPUTS;

let CUISINE_COUNT = 0;

let fatTotal = 0;
let carbsTotal = 0;
let proteinTotal = 0;

// To initialize tooltips and define HIDDEN_INPUTS

$(document).ready(function() {
    $("body").tooltip({ selector: '[data-toggle=tooltip]' });
    HIDDEN_INPUTS = $("[type=hidden]");
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
    fatTotal += $(this).data("fat");
    carbsTotal += $(this).data("carbs");
    proteinTotal += $(this).data("protein");

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
    fatTotal -= $(this).data("fat");
    carbsTotal -= $(this).data("carbs");
    proteinTotal -= $(this).data("protein");
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

//make 3 tracker charts
makeTracker();

}

button.on('click',changeButton);



// NUTRITION CHARTS


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

    // if (percentOfDailyNeeds > 100) {
    //     percentOfDailyNeeds = 100;
    // }

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


function makeNutriDictForTracker(nutrient) {
    let percentOfWeeklyNeeds;
    let color = "#4A7E13";

    if (nutrient === "Fat") {
        percentOfWeeklyNeeds = (fatTotal * 3) / 5;
    }
    else if (nutrient === "Carbs") {
        percentOfWeeklyNeeds = (carbsTotal * 3) / 5;
    }
    if (nutrient === "Protein") {
        percentOfWeeklyNeeds = (proteinTotal * 3) / 5;
    }

    if (percentOfWeeklyNeeds > 100) {
        percentOfWeeklyNeeds = 100;
        color = "#E04732";
    }

    let data_dict = {
                "labels": [
                    nutrient,
                    "remainder"
                ],
                "datasets": [
                    {
                        "data": [percentOfWeeklyNeeds, 100-percentOfWeeklyNeeds],
                        "backgroundColor": [
                            color,
                            "gray"
                        ],
                        "hoverBackgroundColor": [
                            color,
                            "gray"
                        ]
                    }]
            };

    return data_dict;
}

function makeTracker() {
    let fat = makeNutriDictForTracker("Fat");
    let carbs = makeNutriDictForTracker("Carbs");
    let protein = makeNutriDictForTracker("Protein");

    let ctx_donut4 = $("#fatTracker").get(0).getContext("2d");
    let ctx_donut5 = $("#carbsTracker").get(0).getContext("2d");
    let ctx_donut6 = $("#proteinTracker").get(0).getContext("2d");

    makeFatChart(fat, ctx_donut4);
    makeCarbsChart(carbs, ctx_donut5);
    makeProteinChart(protein, ctx_donut6);

}

// $(".nutrition").on('click', makeCharts);



// To initialize popovers


$('[data-toggle="popover"]').popover({
  html: true,
  content: '<canvas id="donutChart1" width="25" height="25"></canvas><canvas id="donutChart2" width="25" height="25"></canvas><canvas id="donutChart3" width="25" height="25"></canvas>',
}).on('shown.bs.popover', makeCharts);


$('.popover-dismiss').popover({
  trigger: 'focus'
});
