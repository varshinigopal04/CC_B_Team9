const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const authRoutes = require('./routes/authRoutes'); // Import routes

dotenv.config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Use routes
app.use('/api/auth', authRoutes);

// MongoDB connection
mongoose.connect(process.env.MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
  .then(() => {
    console.log('✅ MongoDB connected');
    app.listen(3000, () => {
      console.log('🚀 Auth service running on port 3000');
    });
  })
  .catch(err => {
    console.error('❌ Error connecting to MongoDB:', err);
  });
