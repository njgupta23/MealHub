"use strict";

// Toggles between "select" and "saved" buttons 

let button = $(".recipe-select");

function changeButton(evt) {
if (button.html() === "Select") {
  button.html("Saved");
  button.addClass("saved");
} else {
  button.html("Select");
  button.removeClass("saved");
}
}

button.on('click',changeButton);


//      Make a list of all objects from button data.
//      convert that list into json (using javascript)
//      pass the json through the ajax post request to the server

let buttonDataArray = [];
let savedButtons = $(".saved");    // an array of buttons that are saved

for (let i=0; i < length(savedButtons); i++) {
    buttonDataArray.push(savedButtons[i].data());
}

jsonButtonData = JSON.stringify(buttonDataArray);

$.post("/save-recipe", jsonButtonData, )

// recipe_1 = $(...).data()
// .
// .
// .
// result = { data_1: recipe_1, ...}