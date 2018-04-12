"use strict";

// To initialize tooltips

$(document).ready(function() {
    $("body").tooltip({ selector: '[data-toggle=tooltip]' });
});




// Toggles between "select" and "saved" buttons 

let button = $(".recipe-select");

function changeButton(evt) {
if ($(this).html() === "Select") {
  $(this).html("Saved");
  $(this).addClass("saved");
} else {
  $(this).html("Select");
  $(this).removeClass("saved");
}
}

button.on('click',changeButton);


//      Make a list of all objects from button data.
//      convert that list into json (using javascript)
//      pass the json through the ajax post request to the server

// let buttonDataArray = [];
// let savedButtons = $(".saved");    // an array of buttons that are saved

// for (let i=0; i < length(savedButtons); i++) {
//     buttonDataArray.push(savedButtons[i].data());
// }

// jsonButtonData = JSON.stringify(buttonDataArray);

// // add event listener for when "create" button is clicked
// // what should the callback function for the post request be??
// $.post("/save-recipe", jsonButtonData, )

// recipe_1 = $(...).data()
// .
// .
// .
// result = { data_1: recipe_1, ...}