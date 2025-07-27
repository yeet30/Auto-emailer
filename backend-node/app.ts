import express, { Request, Response } from 'express';
import axios from 'axios';

const app = express();

app.use(express.json());

interface Contacts {
  name: string;
  email: string;
  country: string;
  has_website: boolean;
}

interface CampaignBody {
  gmail_address : string;
  app_password : string;
  custom_domain : string;
  text1 : string;
  text2: string;
  subject1: string;
  subject2: string;
  send_hour: number;
  send_minute: number;
  mail_amount: number;
  contacts: Contacts[];
}

app.post('/start-campaign', async (req: Request, res: Response) => {
  const {
    gmail_address,
    app_password,
    custom_domain,
    text1,
    text2,
    subject1,
    subject2,
    send_hour,
    send_minute,
    mail_amount,
    contacts,
  } : CampaignBody= req.body;

  try {
    const response = await axios.post('http://localhost:5000/send', {
      gmail_address,
      app_password,
      custom_domain,
      text1,
      text2,
      subject1,
      subject2,
      send_hour,
      send_minute,
      mail_amount,
      contacts,
    });

    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to forward to Python' });
  }
});

app.listen(3000, () => {
  console.log('Node API running on http://localhost:3000');
});
