
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const orchestrator = require('./services/orchestrator');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.static('public'));

const upload = multer({ dest: 'uploads/' });

app.post('/api/generate', upload.single('song'), async (req, res) => {
  try {
    const { maleName, femaleName } = req.body;
    
    const result = await orchestrator.createVideo(req.file.path, {
      male: maleName || "Jax Blaze",
      female: femaleName || "Luna Vox"
    });

    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`🎥 Super Orchestrator Server running on http://localhost:${PORT}`);
});
