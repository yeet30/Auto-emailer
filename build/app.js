"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const utils_1 = require("./utils");
const app = (0, express_1.default)();
const port = 3000;
app.use(express_1.default.static('public'));
app.use('/build', express_1.default.static('build'));
app.use(express_1.default.json());
app.use((0, cors_1.default)({
    origin: "*",
    methods: ["GET", "POST"],
    allowedHeaders: ["Content-Type"]
}));
app.post('/send', (req, res) => {
    const frontEndData = req.body;
    console.log(frontEndData);
    (0, utils_1.StartEmailCampaign)(frontEndData);
    if (!frontEndData)
        return res.status(403).send({ status: "failed" });
    res.status(200).send({ status: "recieved" });
});
app.listen(port, () => console.log(`Server has started, listening on port ${port}`));
