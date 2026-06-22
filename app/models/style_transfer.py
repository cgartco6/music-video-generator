import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import os

class StyleTransfer:
    def __init__(self, config):
        self.config = config
        self.device = torch.device('cuda' if config.USE_GPU and torch.cuda.is_available() else 'cpu')
        self.model = None
        self.style_image = None
        self._load_model()
        
        # Style mappings for different genres
        self.genre_styles = {
            'rock': 'dark_edgy',
            'pop': 'colorful_vibrant',
            'classical': 'classic_elegant',
            'jazz': 'vintage_warm',
            'electronic': 'neon_futuristic',
            'hiphop': 'urban_street',
            'country': 'rustic_natural',
            'indie': 'indie_alternative'
        }
        
        # Pre-trained style images (in production, load actual images)
        self.style_images = {
            'dark_edgy': self._create_dark_edgy_style(),
            'colorful_vibrant': self._create_colorful_vibrant_style(),
            'classic_elegant': self._create_classic_elegant_style(),
            'vintage_warm': self._create_vintage_warm_style(),
            'neon_futuristic': self._create_neon_futuristic_style(),
            'urban_street': self._create_urban_street_style(),
            'rustic_natural': self._create_rustic_natural_style(),
            'indie_alternative': self._create_indie_style()
        }
    
    def _load_model(self):
        """Load style transfer model"""
        try:
            # In production, load actual style transfer model
            model_path = self.config.STYLE_TRANSFER_MODEL
            if os.path.exists(model_path):
                self.model = torch.load(model_path, map_location=self.device)
            else:
                print(f"Warning: Style transfer model not found at {model_path}")
                print("Using built-in style transfer")
        except Exception as e:
            print(f"Error loading style transfer model: {str(e)}")
            self.model = None
    
    def apply_style(self, video_frames, genre='pop', intensity=0.7):
        """Apply style transfer to video frames"""
        # Get style for genre
        style_name = self.genre_styles.get(genre, 'colorful_vibrant')
        style_image = self.style_images.get(style_name)
        
        if style_image is None:
            return video_frames
        
        styled_frames = []
        
        for frame in video_frames:
            # Apply style to frame
            styled_frame = self._apply_style_to_frame(frame, style_image, intensity)
            styled_frames.append(styled_frame)
        
        return styled_frames
    
    def _apply_style_to_frame(self, frame, style_image, intensity):
        """Apply style transfer to a single frame"""
        # Convert frame to PIL Image
        if isinstance(frame, np.ndarray):
            frame_img = Image.fromarray(frame)
        else:
            frame_img = frame
        
        # Convert to tensor
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
        
        # In production, use actual style transfer model
        # This is a simplified version with filter application
        
        # Apply color filters based on style
        filtered_frame = self._apply_color_filter(frame_img, style_image, intensity)
        
        # Convert back to numpy array
        if isinstance(filtered_frame, Image.Image):
            return np.array(filtered_frame)
        else:
            return filtered_frame
    
    def _apply_color_filter(self, image, style_image, intensity):
        """Apply color filter based on style"""
        # Extract dominant colors from style
        style_colors = self._extract_dominant_colors(style_image)
        
        # Apply color mapping
        filtered = self._apply_color_map(image, style_colors, intensity)
        
        # Apply additional effects based on style
        style_name = self._identify_style(style_image)
        filtered = self._apply_style_effects(filtered, style_name, intensity)
        
        return filtered
    
    def _extract_dominant_colors(self, image):
        """Extract dominant colors from style image"""
        # Simplified color extraction
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image
        
        # Use k-means to find dominant colors
        from sklearn.cluster import KMeans
        pixels = img_array.reshape(-1, 3)
        kmeans = KMeans(n_clusters=5, random_state=42)
        kmeans.fit(pixels)
        return kmeans.cluster_centers_
    
    def _apply_color_map(self, image, colors, intensity):
        """Apply color mapping to image"""
        # Simplified color mapping using PIL
        img = image.copy()
        pixels = np.array(img)
        
        # Create color mapping
        for i, color in enumerate(colors):
            mask = (pixels[:, :, 0] > i * 50) & (pixels[:, :, 0] < (i + 1) * 50)
            for c in range(3):
                pixels[mask, c] = pixels[mask, c] * (1 - intensity) + color[c] * intensity
        
        return Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8))
    
    def _apply_style_effects(self, image, style_name, intensity):
        """Apply additional style-specific effects"""
        from PIL import ImageEnhance, ImageFilter
        
        img = image.copy()
        
        if style_name == 'dark_edgy':
            # Increase contrast, add vignette
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1 + 0.3 * intensity)
            img = self._add_vignette(img, intensity)
            
        elif style_name == 'colorful_vibrant':
            # Increase saturation and contrast
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1 + 0.5 * intensity)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1 + 0.2 * intensity)
            
        elif style_name == 'vintage_warm':
            # Add warm tint and slight blur
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(0.8 + 0.2 * intensity)
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5 * intensity))
            img = self._add_warm_tint(img, intensity)
            
        elif style_name == 'neon_futuristic':
            # Increase saturation, add glow
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1 + 0.6 * intensity)
            img = self._add_neon_glow(img, intensity)
            
        return img
    
    def _add_vignette(self, image, intensity):
        """Add vignette effect"""
        img = image.convert('RGBA')
        width, height = img.size
        
        # Create vignette mask
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        
        # Draw radial gradient
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 2
        for i in range(radius):
            alpha = int(255 * (1 - (i / radius) * intensity))
            draw.ellipse([center_x - i, center_y - i, center_x + i, center_y + i],
                        fill=alpha)
        
        # Apply mask
        img.putalpha(mask)
        return img.convert('RGB')
    
    def _add_warm_tint(self, image, intensity):
        """Add warm tint"""
        img = image.copy()
        pixels = np.array(img)
        
        # Add warm tint (increase red and green, decrease blue)
        tint_intensity = 30 * intensity
        pixels[:, :, 0] = np.clip(pixels[:, :, 0] + tint_intensity, 0, 255)
        pixels[:, :, 1] = np.clip(pixels[:, :, 1] + tint_intensity * 0.5, 0, 255)
        pixels[:, :, 2] = np.clip(pixels[:, :, 2] - tint_intensity * 0.3, 0, 255)
        
        return Image.fromarray(pixels.astype(np.uint8))
    
    def _add_neon_glow(self, image, intensity):
        """Add neon glow effect"""
        img = image.copy()
        pixels = np.array(img)
        
        # Enhance bright areas
        brightness = np.mean(pixels, axis=2)
        glow_mask = brightness > 150
        
        # Add glow to bright areas
        glow_intensity = 50 * intensity
        pixels[glow_mask, 0] = np.clip(pixels[glow_mask, 0] + glow_intensity, 0, 255)
        pixels[glow_mask, 1] = np.clip(pixels[glow_mask, 1] + glow_intensity, 0, 255)
        pixels[glow_mask, 2] = np.clip(pixels[glow_mask, 2] + glow_intensity, 0, 255)
        
        return Image.fromarray(pixels.astype(np.uint8))
    
    def _create_dark_edgy_style(self):
        """Create dark edgy style image"""
        img = Image.new('RGB', (256, 256), (20, 20, 30))
        return img
    
    def _create_colorful_vibrant_style(self):
        """Create colorful vibrant style image"""
        img = Image.new('RGB', (256, 256), (255, 100, 100))
        return img
    
    def _create_classic_elegant_style(self):
        """Create classic elegant style image"""
        img = Image.new('RGB', (256, 256), (200, 180, 150))
        return img
    
    def _create_vintage_warm_style(self):
        """Create vintage warm style image"""
        img = Image.new('RGB', (256, 256), (200, 150, 100))
        return img
    
    def _create_neon_futuristic_style(self):
        """Create neon futuristic style image"""
        img = Image.new('RGB', (256, 256), (0, 255, 255))
        return img
    
    def _create_urban_street_style(self):
        """Create urban street style image"""
        img = Image.new('RGB', (256, 256), (100, 100, 120))
        return img
    
    def _create_rustic_natural_style(self):
        """Create rustic natural style image"""
        img = Image.new('RGB', (256, 256), (120, 100, 80))
        return img
    
    def _create_indie_style(self):
        """Create indie alternative style image"""
        img = Image.new('RGB', (256, 256), (200, 180, 160))
        return img
    
    def _identify_style(self, style_image):
        """Identify style from image"""
        # Simplified style identification
        if isinstance(style_image, np.ndarray):
            avg_color = np.mean(style_image, axis=(0, 1))
        else:
            avg_color = np.mean(np.array(style_image), axis=(0, 1))
        
        # Determine style based on average color
        if avg_color[0] < 50 and avg_color[1] < 50 and avg_color[2] < 50:
            return 'dark_edgy'
        elif avg_color[0] > 200 and avg_color[1] > 200:
            return 'colorful_vibrant'
        elif avg_color[0] > 150 and avg_color[1] > 130 and avg_color[2] < 100:
            return 'vintage_warm'
        elif avg_color[0] < 100 and avg_color[1] > 200 and avg_color[2] > 200:
            return 'neon_futuristic'
        else:
            return 'classic_elegant'
