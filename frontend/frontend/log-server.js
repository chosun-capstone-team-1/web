import express from "express";
import cors from "cors"; // ✅ CORS 미들웨어 추가

const app = express();
const PORT = 4000;

app.use(cors()); // ✅ CORS 허용
app.use(express.json());

app.post("/log", (req, res) => {
    console.log("[Front Log]:", JSON.stringify(req.body, null, 2));
    res.sendStatus(200);
});

app.listen(PORT, () => {
    console.log(`✅ 로그 수집 서버 실행 중 → http://localhost:${PORT}`);
});