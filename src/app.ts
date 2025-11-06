import express from 'express';
import cors from 'cors';
import {StartEmailCampaign} from './utils';

const app = express()
const port = 3000

app.use(express.static('public'))
app.use('/build', express.static('build'));
app.use(express.json());
app.use(cors({
    origin: "*", 
    methods: ["GET", "POST"],
    allowedHeaders: ["Content-Type"]
}));

app.post('/send', (req, res) => {
    const frontEndData = req.body
    console.log(frontEndData);
    StartEmailCampaign(frontEndData);
    
    if (!frontEndData) return res.status(403).send({status: "failed"})
    res.status(200).send({status: "recieved"})
})

app.listen(port, () => console.log(`Server has started, listening on port ${port}`))

