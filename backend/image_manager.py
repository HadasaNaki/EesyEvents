"""
Image Manager for EasyVents
Handles strict folder-based image selection for providers/services
"""

from pathlib import Path
from typing import List, Optional, Dict
import json

class ImageManager:
    """Manages image selection with strict folder-based rules"""
    
    # Category to folder mapping
    CATEGORY_FOLDERS = {
        'hall': 'hall',
        'pool': 'pool',
        'wedding': 'wedding',
        'design': 'design',
        'dj': 'dj',
        'orchestra': 'orchestra',
        'photographers': 'photographers',
        'food': 'food',  # Special: has sub-categories
        'מדינתיים': 'מדינתיים'  # Government/State events - STRICT folder
    }
    
    # Food sub-categories
    FOOD_TYPES = {
        'Milk': 'food/Milk',
        'Meat': 'food/Meat',
        'Neutral': 'food/Neutral'
    }
    
    # Allowed image extensions
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.svg'}
    
    def __init__(self, base_path: str = None):
        """
        Initialize ImageManager
        
        Args:
            base_path: Path to backend/static/images directory
                      If None, auto-detects from __file__ location
        """
        if base_path is None:
            base_path = Path(__file__).parent / 'static' / 'images'
        else:
            base_path = Path(base_path)
            
        self.base_path = base_path
        self._image_cache = {}
        self._load_all_images()
    
    def _load_all_images(self) -> None:
        """Load and cache all available images from folders"""
        # Load category images
        for category, folder in self.CATEGORY_FOLDERS.items():
            if category == 'food':
                continue  # Handle separately
            if category == 'מדינתיים':
                # Load מדינתיים images separately
                self._image_cache[category] = self._get_images_from_folder(folder)
                continue
            self._image_cache[category] = self._get_images_from_folder(folder)
        
        # Load food sub-categories
        for food_type, folder in self.FOOD_TYPES.items():
            key = f'food_{food_type}'
            self._image_cache[key] = self._get_images_from_folder(folder)
    
    def _get_images_from_folder(self, folder_name: str) -> List[str]:
        """
        Get all valid image files from a specific folder
        
        Args:
            folder_name: Folder name (e.g., 'hall', 'food/Milk')
            
        Returns:
            List of image URLs like ['/static/images/hall/img1.jpg', ...]
        """
        folder_path = self.base_path / folder_name
        
        if not folder_path.exists():
            return []
        
        images = []
        for file in sorted(folder_path.iterdir()):
            if file.is_file() and file.suffix.lower() in self.ALLOWED_EXTENSIONS:
                # Create URL path
                relative_path = file.relative_to(self.base_path)
                url = f'/static/images/{relative_path}'.replace('\\', '/')
                images.append(url)
        
        return images
    
    def get_images(
        self, 
        category: str, 
        food_type: Optional[str] = None, 
        count: int = 1
    ) -> List[str]:
        """
        Get images for a category with strict folder rules
        
        Hard Rules:
        - Only returns images from the specified folder
        - Repeats images from SAME folder if needed for variety
        - NEVER mixes images from different folders
        
        Args:
            category: One of 'hall', 'pool', 'wedding', 'design', 'dj', 
                     'orchestra', 'photographers', or 'food'
            food_type: Required if category='food'. One of 'Milk', 'Meat', 'Neutral'
            count: Number of images to return (will repeat if folder has fewer)
            
        Returns:
            List of image URLs (length = count, or less if folder is empty)
            
        Raises:
            ValueError: If invalid category/food_type combination
        """
        # Validate inputs
        if category not in self.CATEGORY_FOLDERS:
            raise ValueError(f"Invalid category: {category}. Must be one of {list(self.CATEGORY_FOLDERS.keys())}")
        
        if category == 'food':
            if food_type is None:
                raise ValueError("food_type is required when category='food'")
            if food_type not in self.FOOD_TYPES:
                raise ValueError(f"Invalid food_type: {food_type}. Must be one of {list(self.FOOD_TYPES.keys())}")
            cache_key = f'food_{food_type}'
        else:
            cache_key = category
        
        # Get available images for this folder
        available_images = self._image_cache.get(cache_key, [])
        
        if not available_images:
            # Return empty list if folder is empty
            return []
        
        # Build result list with repetition if needed
        result = []
        for i in range(count):
            # Cycle through available images
            result.append(available_images[i % len(available_images)])
        
        return result
    
    def get_single_image(
        self, 
        category: str, 
        food_type: Optional[str] = None,
        index: int = 0
    ) -> Optional[str]:
        """
        Get a single image for a category
        
        Hard Rule: ONLY returns images from the correct folder.
        Repeats images from SAME folder if needed.
        Returns None only if folder is completely empty.
        
        Args:
            category: Image category
            food_type: Required for 'food' category
            index: Which image to pick (cycles through available)
            
        Returns:
            Image URL string or None if folder is empty
        """
        images = self.get_images(category, food_type, count=1)
        if images:
            # For cycled access, use modulo
            cache_key = f'food_{food_type}' if category == 'food' else category
            available = self._image_cache.get(cache_key, [])
            if available:
                return available[index % len(available)]
        return None
    
    def get_image_mapping(self) -> Dict[str, List[str]]:
        """
        Get complete mapping of all available images
        
        Returns:
            Dict like {
                'hall': ['/static/images/hall/img1.jpg', ...],
                'pool': [...],
                'food_Milk': [...],
                'food_Meat': [...],
                ...
            }
        """
        return dict(self._image_cache)
    
    def export_manifest(self, output_path: str) -> None:
        """
        Export image manifest as JSON (useful for frontend)
        
        Args:
            output_path: Where to save the JSON manifest
        """
        manifest = {
            'categories': self.CATEGORY_FOLDERS,
            'food_types': self.FOOD_TYPES,
            'images': self.get_image_mapping(),
            'total_images': sum(len(imgs) for imgs in self._image_cache.values())
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    def print_summary(self) -> None:
        """Print summary of available images"""
        print("\n📸 IMAGE MANAGER SUMMARY")
        print("=" * 50)
        
        for category, images in self._image_cache.items():
            count = len(images)
            emoji = "✅" if count > 0 else "⚠️"
            print(f"{emoji} {category.ljust(20)} : {count} images")
        
        total = sum(len(imgs) for imgs in self._image_cache.values())
        print("=" * 50)
        print(f"TOTAL: {total} images across {len(self._image_cache)} folders\n")


# Global instance (initialized in app.py)
image_manager: Optional[ImageManager] = None


def init_image_manager(base_path: str = None) -> ImageManager:
    """Initialize global image manager"""
    global image_manager
    image_manager = ImageManager(base_path)
    return image_manager


def get_images(
    category: str,
    food_type: Optional[str] = None,
    count: int = 1
) -> List[str]:
    """
    Convenience function to get images using global manager
    
    Args:
        category: Image category
        food_type: Required for 'food' category
        count: Number of images
        
    Returns:
        List of image URLs
    """
    if image_manager is None:
        raise RuntimeError("ImageManager not initialized. Call init_image_manager() first")
    return image_manager.get_images(category, food_type, count)


def get_single_image(
    category: str,
    food_type: Optional[str] = None,
    index: int = 0
) -> Optional[str]:
    """
    Convenience function to get single image using global manager
    
    Args:
        category: Image category
        food_type: Required for 'food' category
        index: Which image to pick
        
    Returns:
        Image URL or None
    """
    if image_manager is None:
        raise RuntimeError("ImageManager not initialized. Call init_image_manager() first")
    return image_manager.get_single_image(category, food_type, index)


def get_government_events_images(count: int = 1) -> List[str]:
    """
    Get images for "צווים ואירועים" (Government/State Events)
    
    HARD RULE: Uses ONLY images from static/images/מדינתיים/
    Repeats images if needed, never uses other folders.
    
    Args:
        count: Number of images needed
        
    Returns:
        List of image URLs from מדינתיים folder (repeats if necessary)
    """
    if image_manager is None:
        raise RuntimeError("ImageManager not initialized. Call init_image_manager() first")
    return image_manager.get_images('מדינתיים', count=count)
