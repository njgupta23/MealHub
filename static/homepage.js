"use strict";

// new account form - validate password match

function passwordMatch() {
    let pw = $("#pw").val();
    let confirmPw = $("#confirm_pw").val();

    if (pw !== confirmPw) {
        $("#pw-msg").css("color", "red");
        $("#pw-msg").html("Passwords must match!");
    }
    else {
        $("#pw-msg").css("color", "green");
        $("#pw-msg").html("Match");
    }
}

$("#confirm_pw").keyup(passwordMatch);


// new account form - check for unique email address

function showEmailValidation(results) {
    console.log('results:' + typeof results);

    if (!results) {
        $("#email-msg").css("color", "red");
        $("#email-msg").html("That email is already registered! Try another.");
    }
}

function checkEmailExistence() {
    console.log('checking email');
    $.get("/emails-from-db", {"email": $("#email").val()}, showEmailValidation);

}

$("#email").blur(checkEmailExistence);


// sign in form - validate user credentials

function processCredentials(results) {
    if (!results) {
        
        $("#signin-error").css("color", "red");
        $("#signin-error").html("Incorrect email/password.");
    }
    else {
        $("#si-form").trigger("submit");
    }
}

function checkCredentials(evt) {
    evt.preventDefault();
    console.log("hello");
    let formInputs = {
        "email": $("#si-email").val(),
        "pw": $("#si-pw").val()
    };
    console.log("checking credentials");
    $.get("/check-credentials", formInputs, processCredentials);
}

$("#si-submit").on("click", checkCredentials);
