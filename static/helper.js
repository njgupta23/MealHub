"use strict";

let COUNTER = 0;
let CUISINE_COUNT = 0;
let HIDDEN_INPUTS;


// To initialize tooltips

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

