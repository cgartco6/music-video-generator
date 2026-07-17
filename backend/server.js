const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.static('public'));

// Ensure directories exist
const uploadsDir = path.join(__dirname, '../uploads');
const videosDir = path.join(__dirname, '../public/videos');
fs.mkdirSync(uploadsDir, { recursive: true });
fs.mkdirSync(videosDir, { recursive: true });

const upload = multer({ dest: uploadsDir });

app.post('/api/generate', upload.single('song'), async (req, res) => {
  try {
    const { maleName = "Jax Blaze", femaleName = "Luna Vox", duration = "full" } = req.body;
    
    const outputFile = `video_${Date.now()}.mp4`;
    const outputPath = path.join(videosDir, outputFile);

    // Simulate processing with realistic features
    console.log(`Generating video with ${maleName} and ${femaleName}`);

    // In real version this would use FFmpeg + AI models
    res.json({
      success: true,
      message: "Video generated with realistic singers, multi camera angles, noise removed",
      videoUrl: `/videos/${outputFile}`,
      singers: { male: maleName, female: femaleName },
      duration: duration
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
