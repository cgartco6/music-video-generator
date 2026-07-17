const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(cors());
app.use(express.static('public'));

const upload = multer({ dest: 'uploads/' });

app.post('/generate', upload.single('song'), (req, res) => {
  const { male, female } = req.body;
  const output = path.join('public', 'videos', `video_${Date.now()}.mp4`);
  
  // Simulate processing
  setTimeout(() => {
    res.json({
      success: true,
      message: `Video created with ${male} and ${female}`,
      url: '/videos/output.mp4'
    });
  }, 2000);
});

app.listen(3000, () => console.log('Server started on port 3000'));
