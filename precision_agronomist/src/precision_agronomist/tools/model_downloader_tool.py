from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import gdown
import os
from pathlib import Path


class ModelDownloaderInput(BaseModel):
    """Input schema for ModelDownloader."""
    google_drive_url: str = Field(..., description="Google Drive URL or file ID for the model file")
    destination_path: str = Field(..., description="Local path to save the downloaded model")


class ModelDownloaderTool(BaseTool):
    name: str = "Model Downloader"
    description: str = (
        "Downloads trained model artifacts from Google Drive. "
        "Use this to download ResNet50 classification models and YOLOv8 detection models "
        "before running predictions. Provide either full Google Drive URL or just the file ID."
    )
    args_schema: Type[BaseModel] = ModelDownloaderInput

    def _run(self, google_drive_url: str, destination_path: str) -> str:
        """
        Download model from Google Drive
        
        Args:
            google_drive_url: Full Google Drive URL or file ID
            destination_path: Where to save the file (relative to project root)
        
        Returns:
            Success message with file path
        """
        try:
            # Get absolute path relative to project root
            project_root = Path(__file__).parent.parent.parent.parent.parent
            dest_path = project_root / destination_path
            
            # Create destination directory if it doesn't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Extract file ID from URL if full URL provided
            if 'drive.google.com' in google_drive_url:
                if '/d/' in google_drive_url:
                    file_id = google_drive_url.split('/d/')[-1].split('/')[0]
                elif 'id=' in google_drive_url:
                    file_id = google_drive_url.split('id=')[-1].split('&')[0]
                else:
                    file_id = google_drive_url
                url = f'https://drive.google.com/uc?id={file_id}'
            else:
                # Assume it's already a file ID
                url = f'https://drive.google.com/uc?id={google_drive_url}'
            
            # Download the file
            print(f"Downloading from Google Drive to {dest_path}...")
            gdown.download(url, str(dest_path), quiet=False, fuzzy=True)
            
            if dest_path.exists():
                size_mb = dest_path.stat().st_size / (1024 * 1024)
                return f"✓ Successfully downloaded model to {dest_path} ({size_mb:.2f} MB)"
            else:
                return f"✗ Failed to download model to {dest_path}"
                
        except Exception as e:
            return f"✗ Error downloading model: {str(e)}"

