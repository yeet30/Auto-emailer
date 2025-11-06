"use strict";
const postBtn = document.getElementById('post');
const range = document.getElementById('daily-email-amount');
const output = document.getElementById('range-value');
//Setting up the variables to be used later
const baseURL = "http://localhost:3000/";
const todayDate = new Date();
const todayDateString = dateToString(todayDate);
const maxDate = new Date(todayDate);
maxDate.setMonth(todayDate.getMonth() + 1);
const maxDateString = dateToString(maxDate);
const sending_date = document.getElementById('email-sending-date');
const sending_time = document.getElementById('email-sending-time');
sending_date.setAttribute('min', todayDateString.split("T")[0]); //sets the minimum date to today's date
sending_date.setAttribute('max', maxDateString.split("T")[0]); //sets the maximum date to a month later
//Event Listeners
range.addEventListener('input', () => {
    output.textContent = range.value;
});
postBtn.addEventListener('click', postInfo);
document.addEventListener('DOMContentLoaded', () => {
    sending_date.value = todayDateString.split("T")[0]; //sets the default value to today's date
});
//Functions
async function postInfo(e) {
    e.preventDefault();
    const contactInput = document.getElementById('contact-list');
    const file = contactInput.files?.[0];
    if (!file) {
        alert("Please select a contact list file.");
        return;
    }
    // Read file contents as text
    const text = await file.text();
    let contact_list;
    try {
        contact_list = JSON.parse(text);
    }
    catch (err) {
        alert("Invalid JSON file format.");
        console.error(err);
        return;
    }
    const emailingParameters = {
        base_email: document.getElementById('base-email').value,
        custom_email: document.getElementById('custom-email').value,
        app_password: "REDACTED",
        sender_name: document.getElementById('sender-name').value,
        subject: document.getElementById('subject').value,
        body: document.getElementById('body').value,
    };
    const body = {
        emailingParameters,
        daily_cycle_starting_date: new Date(`${sending_date.value}T${sending_time.value}:00`).getTime(),
        daily_email_amount: range.value,
        email_sent_list: [],
        contact_list
    };
    console.log("Sending:", body);
    body.emailingParameters.app_password = document.getElementById('app-password').value;
    const res = await fetch(baseURL + "send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });
    const result = await res.json().catch(() => null);
    console.log("Response:", result);
}
function dateToString(date) {
    const yyyy = String(date.getFullYear()).padStart(2, '0');
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    const hh = String(date.getHours()).padStart(2, '0');
    const min = String(date.getMinutes()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}T${hh}:${min}`;
}
