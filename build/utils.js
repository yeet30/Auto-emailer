"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SendEmail = SendEmail;
exports.GetLocalTimeInTimezone = GetLocalTimeInTimezone;
exports.DailyEmailListGenerator = DailyEmailListGenerator;
exports.StartEmailCampaign = StartEmailCampaign;
exports.DailyEmailCycle = DailyEmailCycle;
const axios_1 = __importDefault(require("axios"));
async function SendEmail(parca) {
    const response = await axios_1.default.post('http://localhost:5000/send', parca);
    return response.data;
}
function GetLocalTimeInTimezone(timezone) {
    const now = new Date();
    const parts = (type) => new Intl.DateTimeFormat('pl-PL', {
        timeZone: timezone,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    }).formatToParts(now).find(p => p.type === type)?.value;
    return new Date(`${parts('year')}-${parts('month')}-${parts('day')}T${parts('hour')}:${parts('minute')}:${parts('second')}`);
}
function DailyEmailListGenerator(data) {
    //Gets the only daily amount of email amounts to the queue
    const arr = data.contact_list.slice(0, data.daily_email_amount);
    const organizedArr = [];
    //
    for (const contact of arr) {
        contact.local_time = GetLocalTimeInTimezone(contact.time_zone);
        //Gets the time difference between the requested email sending time and the current time (how much has to be waited)
        contact.wait_millisecond = data.daily_cycle_starting_date - contact.local_time.getTime();
        //If it's time has already passed for today, sends it at the same time next day by adding one more day to the date
        if (contact.wait_millisecond < 0)
            contact.wait_millisecond += 86400000; //1 day in miliseconds
        organizedArr.push(contact);
    }
    //Sorts the contacts from whose email sending time is the shortest to the current time to the longest
    organizedArr.sort((a, b) => a.wait_millisecond - b.wait_millisecond);
    const length = organizedArr.length;
    /*Checks if there are any duplicate waiting times, if there are any that means they are from the same time zone.
    Sets the duplicates to zero (0) except for the on in the first index, that way it does all the waiting for the ones
    in the same time zone, by itself*/
    for (let i = 0; i < length; i++) {
        for (let j = i + 1; j < length; j++)
            if (organizedArr[j].wait_millisecond == organizedArr[i].wait_millisecond && organizedArr[i].wait_millisecond != 0)
                organizedArr[j].wait_millisecond = 0;
    }
    //Returns the sorted daily list
    return organizedArr;
}
//Returns the next cycle waiting amount and the list of contacts that had been emailed to
async function StartEmailCampaign(frontEndRequest) {
    const emailingParameters = frontEndRequest.emailingParameters;
    const emailSentList = [];
    const emailFailedtoSendList = [];
    const cycleAmount = frontEndRequest.contact_list.length / frontEndRequest.daily_email_amount;
    for (let i = 0; i < cycleAmount; i++) {
        const dailyEmailList = DailyEmailListGenerator(frontEndRequest);
        const [nextCycleWaitTimeMS, dailyEmailSentList, dailyEmailFailedtoSendList] = await DailyEmailCycle(dailyEmailList, emailingParameters);
        emailSentList.push(dailyEmailSentList);
        emailFailedtoSendList.push(dailyEmailFailedtoSendList);
        //Sleeps until the start of the new cycle
        await new Promise(resolve => setTimeout(resolve, nextCycleWaitTimeMS));
    }
}
async function DailyEmailCycle(dailyEmailList, emailingParameters) {
    //Initializing the variables to be used for both logging and to manage timing
    const currentTime = new Date();
    const tomorrowTime = new Date();
    tomorrowTime.setDate(currentTime.getDate() + 1);
    const nextCycleStartTimeMS = tomorrowTime.getTime();
    const currentTimeString = `${currentTime.getHours()}:${currentTime.getMinutes()}`;
    console.log(`The email campaign has started at ${currentTimeString}`);
    console.log("The emails list for today: ", dailyEmailList);
    //Initializing the blacklist of contacts to be returned
    const emailSentList = [];
    const emailCouldNotSentList = [];
    for (const contact of dailyEmailList) { //Goes through the daily list of contacts to email to
        const nextMailDateString = new Date((new Date().getTime() + contact.wait_millisecond)).toLocaleString('pl-PL', {
            timeZone: 'Europe/Warsaw',
            hour: '2-digit',
            minute: '2-digit',
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
        console.log("The next email will be sent in ", Math.floor(contact.wait_millisecond / 3600000), " hours, ", Math.floor((contact.wait_millisecond % 3600000) / 60000), " minutes and ", Math.floor((contact.wait_millisecond % 60000) / 1000), " seconds to: ", contact.name, " in ", contact.country, " at ", nextMailDateString, " in this computer.");
        //Waits for the appropiate time to send the email for each contact
        await new Promise(resolve => setTimeout(resolve, contact.wait_millisecond));
        //Gets the email address of the contact and puts it into the emailing parameters
        emailingParameters.to_email = contact.email;
        //Gets the emailerAPI's response which is in a JSON format
        const emailerAPIResponse = await SendEmail(emailingParameters);
        console.log(emailerAPIResponse.status);
        //If the response states that the email has been sent, it puts it into the blacklist
        if (emailerAPIResponse.isSent) {
            emailSentList.push(contact);
        }
        else
            emailCouldNotSentList.push(contact);
    }
    console.log("Campaign ended, emails sent to: ", emailSentList);
    //Calculates the time needed to be waited for the start of the next cycle
    const nextCycleWaitTimeMS = nextCycleStartTimeMS - currentTime.getTime();
    return [nextCycleWaitTimeMS, emailSentList, emailCouldNotSentList];
}
