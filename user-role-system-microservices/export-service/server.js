const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const jwt = require('jsonwebtoken');
const axios = require('axios');
const { Parser } = require('json2csv');
dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const PORT = 5004;

// 🔐 Auth Middleware
const auth = (req, res, next) => {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.status(401).json({ error: "No token" });

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch {
    res.status(401).json({ error: "Invalid token" });
  }
};

// 🧑‍💻 Admin-only Middleware
const adminOnly = (req, res, next) => {
  if (req.user.role !== 'admin') return res.status(403).json({ error: "Admins only" });
  next();
};

// 🌐 Base URLs of other services
const USER_SERVICE = 'http://localhost:5001/users';
const FEEDBACK_SERVICE = 'http://localhost:5003/feedback';
const ISSUE_SERVICE = 'http://localhost:5002/issues';

// 📁 Export as JSON
app.get('/export/json', auth, adminOnly, async (req, res) => {
  try {
    const [users, issues, feedbacks] = await Promise.all([
      axios.get(USER_SERVICE, { headers: req.headers }),
      axios.get(ISSUE_SERVICE, { headers: req.headers }),
      axios.get(FEEDBACK_SERVICE, { headers: req.headers })
    ]);

    res.json({
      users: users.data,
      issues: issues.data,
      feedbacks: feedbacks.data
    });
  } catch (err) {
    res.status(500).json({ error: "Data export failed", details: err.message });
  }
});

// 📁 Export as CSV
app.get('/export/csv', auth, adminOnly, async (req, res) => {
  try {
    const [users, issues, feedbacks] = await Promise.all([
      axios.get(USER_SERVICE, { headers: req.headers }),
      axios.get(ISSUE_SERVICE, { headers: req.headers }),
      axios.get(FEEDBACK_SERVICE, { headers: req.headers })
    ]);

    const csvUsers = new Parser().parse(users.data);
    const csvIssues = new Parser().parse(issues.data);
    const csvFeedbacks = new Parser().parse(feedbacks.data);

    res.setHeader('Content-Type', 'text/csv');
    res.attachment('export.csv');
    res.send(`--- USERS ---\n${csvUsers}\n\n--- ISSUES ---\n${csvIssues}\n\n--- FEEDBACK ---\n${csvFeedbacks}`);
  } catch (err) {
    res.status(500).json({ error: "CSV export failed", details: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Export service running on port ${PORT}`);
});
