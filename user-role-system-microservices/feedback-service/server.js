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
  console.log('✅ Feedback Service connected to MongoDB');
  app.listen(5003, () => console.log('🚀 Feedback Service running on port 5003'));
}).catch(err => console.error('❌ MongoDB Error:', err));

// Auth Middleware
const auth = (req, res, next) => {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.status(401).json({ error: "No token provided" });

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch {
    res.status(401).json({ error: "Invalid token" });
  }
};

// Feedback Schema
const Feedback = mongoose.model('Feedback', new mongoose.Schema({
  message: String,
  submittedBy: String,
  submittedAt: { type: Date, default: Date.now }
}));

// ✍️ Submit Feedback
app.post('/feedback', auth, async (req, res) => {
  const { message } = req.body;
  const feedback = new Feedback({ message, submittedBy: req.user.email });
  await feedback.save();
  res.json({ message: "Feedback submitted", feedback });
});

// 👀 View all Feedback (admin only)
app.get('/feedback', auth, async (req, res) => {
  if (req.user.role !== 'admin') return res.status(403).json({ error: "Admins only" });
  const feedbacks = await Feedback.find();
  res.json(feedbacks);
});
