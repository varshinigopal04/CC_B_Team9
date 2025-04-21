const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const jwt = require('jsonwebtoken');
dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Connect to MongoDB
mongoose.connect(process.env.MONGO_URI).then(() => {
  console.log('✅ Issue Service connected to MongoDB');
  app.listen(5002, () => console.log('🚀 Issue Service running on port 5002'));
}).catch(err => console.error('❌ MongoDB Error:', err));

// Middleware to check token
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

// Schema
const Issue = mongoose.model('Issue', new mongoose.Schema({
  title: String,
  description: String,
  createdBy: String,
  createdAt: { type: Date, default: Date.now }
}));

// 🚨 Report a new issue
app.post('/issues', auth, async (req, res) => {
  const { title, description } = req.body;
  const issue = new Issue({ title, description, createdBy: req.user.email });
  await issue.save();
  res.json({ message: "Issue submitted successfully", issue });
});

// 🧾 Get all issues (admin only)
app.get('/issues', auth, async (req, res) => {
  if (req.user.role !== 'admin') return res.status(403).json({ error: "Only admins can view issues" });
  const issues = await Issue.find();
  res.json(issues);
});
