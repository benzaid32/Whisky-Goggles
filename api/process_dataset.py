import os
import glob
import argparse
import json
from tqdm import tqdm
import shutil
from PIL import Image
from models.image_processor import WhiskyBottleProcessor
from utils.database import BottleDatabase

def extract_bottle_name(filename):
    """Extract bottle name from filename."""
    # Remove extension and path
    basename = os.path.basename(filename)
    name = os.path.splitext(basename)[0]
    
    # Handle special formats if needed
    # For now, just replace underscores with spaces
    name = name.replace('_', ' ').replace('-', ' ')
    
    return name

def process_dataset(input_dir, output_dir, metadata_file):
    """
    Process all bottle images in the dataset and generate embeddings.
    
    Args:
        input_dir: Directory containing bottle images
        output_dir: Directory to save embeddings
        metadata_file: Path to save metadata JSON
    """
    # Ensure output directories exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
    
    # Initialize image processor and database
    processor = WhiskyBottleProcessor()
    database = BottleDatabase(embeddings_dir=output_dir, metadata_file=metadata_file)
    
    # Get all image files
    image_files = []
    for ext in ['jpg', 'jpeg', 'png']:
        image_files.extend(glob.glob(os.path.join(input_dir, f"*.{ext}")))
        image_files.extend(glob.glob(os.path.join(input_dir, f"*.{ext.upper()}")))
    
    print(f"Found {len(image_files)} images in {input_dir}")
    
    # Process each image
    for image_file in tqdm(image_files, desc="Processing images"):
        try:
            # Generate a unique ID for the bottle
            bottle_id = os.path.splitext(os.path.basename(image_file))[0]
            
            # Extract bottle name
            bottle_name = extract_bottle_name(image_file)
            
            # Extract features
            features = processor.extract_features(image_file)
            
            # Add to database
            database.add_bottle(
                bottle_id=bottle_id,
                name=bottle_name,
                features=features,
                image_url=f"images/{os.path.basename(image_file)}",
                save=True
            )
            
            # Print progress
            print(f"Processed {bottle_name}")
            
        except Exception as e:
            print(f"Error processing {image_file}: {e}")
    
    # Save the FAISS index
    database.save_index()
    
    print(f"Processing complete. Processed {len(database.metadata)} bottles.")
    print(f"Metadata saved to {metadata_file}")
    print(f"Embeddings saved to {output_dir}")
    print(f"FAISS index saved to data/faiss.index")

def copy_images(input_dir, output_dir):
    """Copy images to the web server's static directory."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files
    image_files = []
    for ext in ['jpg', 'jpeg', 'png']:
        image_files.extend(glob.glob(os.path.join(input_dir, f"*.{ext}")))
        image_files.extend(glob.glob(os.path.join(input_dir, f"*.{ext.upper()}")))
    
    # Copy each image
    for image_file in tqdm(image_files, desc="Copying images"):
        try:
            shutil.copy2(image_file, os.path.join(output_dir, os.path.basename(image_file)))
        except Exception as e:
            print(f"Error copying {image_file}: {e}")
    
    print(f"Copied {len(image_files)} images to {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process whisky bottle dataset")
    parser.add_argument("--input", "-i", required=True, help="Input directory with bottle images")
    parser.add_argument("--output", "-o", default="data/embeddings", help="Output directory for embeddings")
    parser.add_argument("--metadata", "-m", default="data/metadata.json", help="Output file for metadata")
    parser.add_argument("--copy-images", "-c", action="store_true", help="Copy images to static directory")
    parser.add_argument("--image-output", default="static/images", help="Output directory for images")
    
    args = parser.parse_args()
    
    # Process dataset
    process_dataset(args.input, args.output, args.metadata)
    
    # Copy images if requested
    if args.copy_images:
        copy_images(args.input, args.image_output) 