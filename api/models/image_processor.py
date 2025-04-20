import os
import torch
import numpy as np
from PIL import Image
import cv2
from transformers import CLIPProcessor, CLIPModel

class WhiskyBottleProcessor:
    """
    Processes whisky bottle images using OpenAI's CLIP model
    to extract feature embeddings.
    """
    
    def __init__(self, model_name="openai/clip-vit-base-patch32"):
        """
        Initialize the CLIP model and processor.
        
        Args:
            model_name: Hugging Face model name for CLIP
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load CLIP model and processor
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        
        # Set model to evaluation mode
        self.model.eval()
        
        print(f"Loaded CLIP model: {model_name}")
    
    def preprocess_image(self, image):
        """
        Preprocess image for better recognition:
        - Convert to RGB if needed
        - Perform image enhancements (lighting correction, etc.)
        
        Args:
            image: PIL Image or file path
            
        Returns:
            Preprocessed PIL Image
        """
        # Load image if it's a file path
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        elif not isinstance(image, Image.Image):
            raise ValueError("Image must be a PIL Image, file path, or numpy array")
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # No heavy preprocessing to let CLIP work with its expected input
        return image
    
    def extract_features(self, image):
        """
        Extract feature embeddings from an image using CLIP.
        
        Args:
            image: PIL Image or file path
            
        Returns:
            Feature vector (numpy array)
        """
        # Preprocess the image
        processed_image = self.preprocess_image(image)
        
        # Process image with CLIP
        with torch.no_grad():
            inputs = self.processor(
                images=processed_image,
                return_tensors="pt"
            ).to(self.device)
            
            # Extract image features
            features = self.model.get_image_features(**inputs)
            
            # Normalize features to unit length
            features = features / features.norm(dim=-1, keepdim=True)
            
            # Convert to numpy array
            features_np = features.cpu().numpy().flatten()
        
        return features_np
    
    def compute_batch_features(self, image_paths):
        """
        Compute features for a batch of images.
        
        Args:
            image_paths: List of file paths to images
            
        Returns:
            Dictionary mapping file paths to feature vectors
        """
        features_dict = {}
        
        for path in image_paths:
            try:
                features = self.extract_features(path)
                features_dict[path] = features
                print(f"Processed {path}")
            except Exception as e:
                print(f"Error processing {path}: {e}")
        
        return features_dict 