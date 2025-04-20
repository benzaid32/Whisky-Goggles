# Whisky Bottle Recognition API

A computer vision API for identifying whisky bottles from images. This API uses OpenAI's CLIP model for feature extraction and FAISS for efficient similarity search.

## Features

- Image recognition for whisky bottles
- Confidence scoring for matches
- REST API with FastAPI
- Docker containerization for easy deployment
- AWS EC2 deployment support

## Requirements

- Python 3.9+
- Docker (for containerized deployment)
- 500+ MB disk space for model and embeddings
- A dataset of whisky bottle images

## Quick Start

### Local Development

1. Clone the repository:
   ```
   git clone <your-repo-url>
   cd api
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Process your dataset of bottle images:
   ```
   python process_dataset.py --input /path/to/images --output data/embeddings --metadata data/metadata.json --copy-images
   ```

5. Run the API:
   ```
   python run.py
   ```

The API will be available at http://localhost:8000

### Docker Deployment

1. Build and run with Docker Compose:
   ```
   docker-compose up -d
   ```

2. Process your dataset of bottle images:
   ```
   docker-compose exec api python process_dataset.py --input /path/to/images --output data/embeddings --metadata data/metadata.json --copy-images
   ```

The API will be available at http://localhost:8000

## API Endpoints

### `GET /`

Health check endpoint.

### `POST /api/identify`

Identify a whisky bottle from an uploaded image.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: 
  - `file`: Image file (JPEG, PNG)

**Response:**
```json
{
  "matches": [
    {
      "id": "bottle1",
      "name": "Glenlivet 12",
      "confidence": 0.95,
      "image_url": "images/glenlivet12.jpg"
    },
    {
      "id": "bottle2",
      "name": "Macallan 15",
      "confidence": 0.82,
      "image_url": "images/macallan15.jpg"
    }
  ],
  "processing_time_ms": 125.5
}
```

### `POST /api/identify_base64`

Identify a whisky bottle from a base64-encoded image (for mobile apps).

**Request:**
- Method: POST
- Content-Type: application/json
- Body:
  ```json
  {
    "base64_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABA..."
  }
  ```

**Response:** Same as the `/api/identify` endpoint.

### `GET /api/bottles`

List all bottles in the database.

**Response:**
```json
[
  {
    "id": "bottle1",
    "name": "Glenlivet 12",
    "confidence": 1.0,
    "image_url": "images/glenlivet12.jpg"
  },
  {
    "id": "bottle2",
    "name": "Macallan 15",
    "confidence": 1.0,
    "image_url": "images/macallan15.jpg"
  }
]
```

## AWS EC2 Deployment

See the [AWS Deployment Guide](AWS_DEPLOYMENT.md) for detailed instructions on deploying to AWS EC2.

## React Native Integration

Example code to call the API from a React Native app:

```javascript
import * as ImagePicker from 'expo-image-picker';

const identifyBottle = async () => {
  try {
    // Launch camera or image picker
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
    });
    
    if (!result.cancelled) {
      // Create form data
      const formData = new FormData();
      formData.append('file', {
        uri: result.uri,
        type: 'image/jpeg',
        name: 'bottle.jpg',
      });
      
      // Send to API
      const response = await fetch('https://your-api-endpoint.com/api/identify', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        },
      });
      
      // Parse response
      const data = await response.json();
      console.log('Matches:', data.matches);
      
      // Use matches in your app
      return data.matches;
    }
  } catch (error) {
    console.error('Error identifying bottle:', error);
  }
};
```

## License

[Specify your license here]

## Acknowledgements

- [OpenAI CLIP](https://github.com/openai/CLIP)
- [FAISS](https://github.com/facebookresearch/faiss)
- [FastAPI](https://fastapi.tiangolo.com/) 