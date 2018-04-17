"use strict";


// Nutrition charts for saved recipes


let ctx_donut7 = $("#fatTotal").get(0).getContext("2d");
let ctx_donut8 = $("#carbsTotal").get(0).getContext("2d");
let ctx_donut9 = $("#proteinTotal").get(0).getContext("2d");

$.get("/fat-data.json", function(data) {
    let fatTotalChart = new Chart(ctx_donut7, {
                            type: "doughnut",
                            data: data,
                            options: {
                                        legend: {
                                                display: false
                                        },
                                        title: {
                                                display: true,
                                                text: 'Fat'
                                            },
                                        responsive: true
                                    }
    });
});

$.get("/carbs-data.json", function(data) {
    let carbsTotalChart = new Chart(ctx_donut8, {
                            type: "doughnut",
                            data: data,
                            options: {
                                        legend: {
                                                display: false
                                        },
                                        title: {
                                                display: true,
                                                text: 'Carbs'
                                            },
                                        responsive: true
                                    }
    });
});

$.get("/protein-data.json", function(data) {
    let proteinTotalChart = new Chart(ctx_donut9, {
                            type: "doughnut",
                            data: data,
                            options: {
                                        legend: {
                                                display: false
                                        },
                                        title: {
                                                display: true,
                                                text: 'Protein'
                                            },
                                        responsive: true
                                    }
    });
});