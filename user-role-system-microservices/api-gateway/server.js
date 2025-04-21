const express = require("express");
const cors = require("cors");
const { createProxyMiddleware } = require("http-proxy-middleware");
const dotenv = require("dotenv");
dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const PORT = 8080;

// 👇 Routing and proxy setup
app.use("/api/auth", createProxyMiddleware({
    target: "http://localhost:5000",
    changeOrigin: true,
    pathRewrite: { "^/api/auth": "" },
}));

app.use("/api/users", createProxyMiddleware({
    target: "http://localhost:5001",
    changeOrigin: true,
    pathRewrite: { "^/api/users": "" },
}));

app.use("/api/issues", createProxyMiddleware({
    target: "http://localhost:5002",
    changeOrigin: true,
    pathRewrite: { "^/api/issues": "" },
}));

app.use("/api/feedback", createProxyMiddleware({
    target: "http://localhost:5003",
    changeOrigin: true,
    pathRewrite: { "^/api/feedback": "" },
}));

app.use("/api/export", createProxyMiddleware({
    target: "http://localhost:5004",
    changeOrigin: true,
    pathRewrite: { "^/api/export": "" },
}));

app.listen(PORT, () => {
    console.log(`🚪 API Gateway running at http://localhost:${PORT}`);
});
