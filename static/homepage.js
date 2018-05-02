"use strict";

// new account form validation

//need ajax request for email check
// use ids to compare the passwords in both pw fields
// add empty divs for error messages

if ($("#pw1").val !== $("#pw2").val) {
    $("#pw-msg").html("<p>Does not match password.</p>");
}