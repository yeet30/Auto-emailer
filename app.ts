import express, { Request, Response } from 'express';
import cors from 'cors';
import axios from 'axios';

const app = express()
const port = 3000

async function SendEmail(parca: Record<string,any>){ //Sends the json to python's api
    const response = await axios.post('http://localhost:5000/send', parca);
    return response.data;
}

function getLocalTimeInTimezone(timezone: string){ //returns the current local time in the given timezone
    const now = new Date();
    const parts = (type: string) => new Intl.DateTimeFormat('pl-PL', {
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

function ListOrganizer(data: any){
    const arr = data.contact_list.slice(0,data.daily_email_amount)
    data.contact_list.splice(0,data.daily_email_amount)
    const organizedArr=[]
    for(const contact of arr){
        contact.local_time = getLocalTimeInTimezone(contact.time_zone)
        contact.wait_millisecond = data.daily_cycle_starting_date - contact.local_time.getTime()
        if(contact.wait_millisecond<0)
            contact.wait_millisecond += 86400000
        contact.wait_hours = Math.floor(contact.wait_millisecond/3600000)
        organizedArr.push(contact)
    }
    organizedArr.sort((a,b) => a.wait_millisecond - b.wait_millisecond)
    data.daily_email_list = organizedArr
}

async function startEmailCampaign(data: any){
    const arr = data.daily_email_list;
    const currentTime = new Date();
    const tomorrowTime = new Date();
    tomorrowTime.setDate(currentTime.getDate()+1)
    const nextCycleStartTimeMS = tomorrowTime.getTime()
    const currentTimeString = `${currentTime.getHours()}:${currentTime.getMinutes()}`;
    console.log(`The email campaign has started at ${currentTimeString}`)
    console.log("The emails list for today: ", arr)
    data.email_sent_list = []
    

    for (const contact of arr){
        const nextMailDateString = new Date((new Date().getTime() + contact.wait_millisecond)).toLocaleString('pl-PL',{
            timeZone: 'Europe/Warsaw',
            hour: '2-digit',
            minute: '2-digit',
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        })
        console.log("The next email will be sent in ", Math.floor(contact.wait_millisecond/3600000),
            " hours, " , Math.floor((contact.wait_millisecond % 3600000) / 60000), 
            " minutes and " , Math.floor((contact.wait_millisecond % 60000) / 1000),
            " seconds to: " , contact.name, " in ",contact.country ,
            " at ", nextMailDateString , " in this computer.")
        await new Promise(resolve => setTimeout(resolve, contact.wait_millisecond))
        const reqData = data
        delete reqData.contact_list
        reqData.to_email = contact.email
        const responseAPI = await SendEmail(reqData)
        console.log(responseAPI.status);
        if(responseAPI.isSent){
            data.email_sent_list.push(contact)
        }
    }
    
    console.log("Campaign ended, emails sent to: ", data.email_sent_list)
    const nextCycleWaitTimeMS = nextCycleStartTimeMS - currentTime.getTime()
    await new Promise(resolve => setTimeout(resolve, nextCycleWaitTimeMS))
}

app.use(express.static('public'))
app.use(express.json());
app.use(cors({
    origin: "*", 
    methods: ["GET", "POST"],
    allowedHeaders: ["Content-Type"]
}));

app.post('/send', (req, res) => {
    const frontEndData = req.body
    console.log(frontEndData);
    ListOrganizer(frontEndData);
    startEmailCampaign(frontEndData);
    
    if (!frontEndData) return res.status(403).send({status: "failed"})
    res.status(200).send({status: "recieved"})
})

app.listen(port, () => console.log(`Server has started, listening on port ${port}`))

