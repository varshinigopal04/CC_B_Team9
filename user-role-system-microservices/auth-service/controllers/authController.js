// auth-service/controllers/authController.js

const bcrypt = require('bcrypt');
const User = require('../models/User');  // Assuming you're using mongoose

// Register User function
const registerUser = async (req, res) => {
  const { name, email, password, role } = req.body;

  try {
    // Check if user already exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ message: 'User already exists' });
    }

    // Hash the password before saving
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create a new user object
    const newUser = new User({
      name,
      email,
      password: hashedPassword,
      role
    });

    // Save the new user to the database
    await newUser.save();

    // Respond with success message
    res.status(201).json({
      message: 'User registered successfully',
      user: { name, email, role }  // Returning user details without password
    });
  } catch (err) {
    res.status(500).json({ message: 'Server error', error: err.message });
  }
};

module.exports = { registerUser };
