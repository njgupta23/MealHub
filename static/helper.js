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
console.log("this is the counter before changeButton: " + COUNTER);
function changeButton(evt) {
if ($(this).html() === "Select") {
    $(this).html("Saved");
    $(this).addClass("saved");
    COUNTER += 1;
    let buttonData = $(this).data();    // a dict
    console.log("buttonData id is " + buttonData["id"]);

    $(HIDDEN_INPUTS[COUNTER-1]).attr("value", JSON.stringify(buttonData));
    console.log("this is the counter after saving a recipe: " + COUNTER);
    console.log(HIDDEN_INPUTS[0]);
    } else {
    $(this).html("Select");
    $(this).removeClass("saved");
    $(HIDDEN_INPUTS[COUNTER-1]).attr("name", "");
    $(HIDDEN_INPUTS[COUNTER-1]).attr("value", "");
    COUNTER -= 1;
    console.log("this is the counter after unsaving a recipe: " + COUNTER);
    console.log(HIDDEN_INPUTS[0]);
    }

if (COUNTER === 5) {
    $("#create").css("visibility", "visible");
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
