"use strict";

let COUNTER = 0;
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


// Toggles between "select" and "saved" buttons 

let button = $(".recipe-select");

function changeButton(evt) {
if ($(this).html() === "Select") {
    COUNTER += 1;
    $(this).html("Saved for Day " + COUNTER);
    $(this).removeClass("unsaved");
    $(this).addClass("saved");
    let buttonData = $(this).data();    // a dict
    $(HIDDEN_INPUTS[COUNTER-1]).attr("value", JSON.stringify(buttonData));
    } 

else {
    $(this).html("Select");
    $(this).removeClass("saved");
    $(this).addClass("unsaved");
    $(HIDDEN_INPUTS[COUNTER-1]).attr("name", "");
    $(HIDDEN_INPUTS[COUNTER-1]).attr("value", "");
    COUNTER -= 1;
    }

if (COUNTER === 5) {
    $("#create").css("visibility", "visible");
    $(".unsaved").css("visibility", "hidden");
    }

else {
    $(".unsaved").css("visibility", "visible");
}
}

button.on('click',changeButton);




//      // Make a list of all objects from button data.
//      // convert that list into json (using javascript)
//      // pass the json through the ajax post request to the server

// let buttonDataArray = [];
// let savedButtons = $(".saved");    // an array of buttons that are saved

// for (let i=0; i < length(savedButtons); i++) {
//     buttonDataArray.push(savedButtons[i].data());
// }

// jsonButtonData = JSON.stringify(buttonDataArray);

// // add event listener for when "create" button is clicked
// // what should the callback function for the post request be??
// $.post("/save-recipe", jsonButtonData, )

// // recipe_1 = $(...).data()
// // .
// // .
// // .
// // result = { data_1: recipe_1, ...}
