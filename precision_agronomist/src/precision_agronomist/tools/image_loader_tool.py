from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from pathlib import Path
import random
import json


class ImageLoaderInput(BaseModel):
    """Input schema for ImageLoader."""
    test_dir: str = Field(
        default="data/test",
        description="Directory containing test images (relative to project root)"
    )
    num_images: int = Field(
        default=5,
        description="Number of images to load"
    )
    random_selection: bool = Field(
        default=True,
        description="Randomly select images or use first N"
    )


class ImageLoaderTool(BaseTool):
    name: str = "Test Image Loader"
    description: str = (
        "Loads test images from the data/test directory for plant disease analysis. "
        "Can select images randomly or sequentially. Returns absolute paths to selected images."
    )
    args_schema: Type[BaseModel] = ImageLoaderInput

    def _run(
        self, 
        test_dir: str = "data/test", 
        num_images: int = 5,
        random_selection: bool = True
    ) -> str:
        """
        Load test images for prediction
        
        Args:
            test_dir: Directory with test images (relative to project root)
            num_images: How many images to load
            random_selection: Random or sequential selection
            
        Returns:
            List of image paths as JSON string
        """
        try:
            # Get absolute path relative to project root
            project_root = Path(__file__).parent.parent.parent.parent.parent
            test_path = project_root / test_dir
            
            if not test_path.exists():
                return json.dumps({
                    "status": "error",
                    "message": f"Test directory not found: {test_path}"
                })
            
            # Get all image files
            image_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
            all_images = [
                str(img.absolute()) for img in test_path.iterdir() 
                if img.suffix in image_extensions and img.is_file()
            ]
            
            if not all_images:
                return json.dumps({
                    "status": "error",
                    "message": f"No images found in {test_path}"
                })
            
            # Select images
            if random_selection:
                selected_images = random.sample(
                    all_images, 
                    min(num_images, len(all_images))
                )
            else:
                selected_images = all_images[:num_images]
            
            result = {
                "status": "success",
                "test_directory": str(test_path),
                "total_images_available": len(all_images),
                "selected_count": len(selected_images),
                "selected_images": selected_images
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": str(e)
            })

