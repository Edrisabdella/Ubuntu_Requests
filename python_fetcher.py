import requests
import os
import hashlib
from urllib.parse import urlparse
from typing import List, Optional

class UbuntuImageFetcher:
    def __init__(self):
        self.downloaded_hashes = set()
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit for safety
        
    def print_welcome(self):
        print("Welcome to the Ubuntu Image Fetcher")
        print("A tool for mindfully collecting images from the web")
        print("Ubuntu: 'I am because we are'")
        print("-" * 50)
        
    def get_user_urls(self) -> List[str]:
        """Prompt user for URLs, supporting multiple inputs"""
        urls_input = input("Please enter image URL(s), separated by commas: ").strip()
        if not urls_input:
            return []
        
        # Split by commas and clean up whitespace
        urls = [url.strip() for url in urls_input.split(',')]
        return [url for url in urls if url]  # Remove empty strings
    
    def is_safe_url(self, url: str) -> bool:
        """Check if URL uses a safe scheme"""
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https')
    
    def get_filename_from_url(self, url: str, content_type: str) -> str:
        """Extract filename from URL or generate one based on content type"""
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        
        if not filename:
            # Generate a filename based on content type
            extension = self.get_extension_from_content_type(content_type)
            filename = f"ubuntu_image{extension}"
        else:
            # Ensure the filename has an appropriate extension
            _, ext = os.path.splitext(filename)
            if not ext:
                extension = self.get_extension_from_content_type(content_type)
                filename += extension
        
        return filename
    
    def get_extension_from_content_type(self, content_type: str) -> str:
        """Map content type to file extension"""
        content_map = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/svg+xml': '.svg',
            'image/bmp': '.bmp',
            'image/tiff': '.tiff'
        }
        return content_map.get(content_type, '.jpg')  # Default to jpg
    
    def is_duplicate_image(self, content: bytes) -> bool:
        """Check if we've already downloaded this image using hash"""
        content_hash = hashlib.md5(content).hexdigest()
        if content_hash in self.downloaded_hashes:
            return True
        self.downloaded_hashes.add(content_hash)
        return False
    
    def validate_response(self, response: requests.Response) -> bool:
        """Validate the HTTP response before processing"""
        # Check status code
        if response.status_code != 200:
            return False
            
        # Check content type is an image
        content_type = response.headers.get('Content-Type', '').lower()
        if not content_type.startswith('image/'):
            return False
            
        # Check content length isn't too large
        content_length = response.headers.get('Content-Length')
        if content_length and int(content_length) > self.max_file_size:
            return False
            
        return True
    
    def download_image(self, url: str) -> Optional[str]:
        """Download a single image from a URL"""
        if not self.is_safe_url(url):
            print(f"✗ Unsafe URL scheme: {url}")
            return None
            
        try:
            # Make request with appropriate headers and timeout
            headers = {
                'User-Agent': 'UbuntuImageFetcher/1.0 (Community-Friendly Image Collector)'
            }
            response = requests.get(url, headers=headers, timeout=15, stream=True)
            
            # Validate response before processing
            if not self.validate_response(response):
                print(f"✗ Invalid response from {url}")
                return None
                
            # Read content in chunks to handle large files safely
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > self.max_file_size:
                    print(f"✗ File too large: {url}")
                    return None
                    
            # Check for duplicates
            if self.is_duplicate_image(content):
                print(f"⚠ Already downloaded: {url}")
                return None
                
            # Get filename and save
            content_type = response.headers.get('Content-Type', '').lower()
            filename = self.get_filename_from_url(url, content_type)
            filepath = os.path.join("Fetched_Images", filename)
            
            # Ensure unique filename if file already exists
            counter = 1
            base, ext = os.path.splitext(filepath)
            while os.path.exists(filepath):
                filepath = f"{base}_{counter}{ext}"
                counter += 1
                
            with open(filepath, 'wb') as f:
                f.write(content)
                
            print(f"✓ Successfully fetched: {filename}")
            print(f"✓ Image saved to {filepath}")
            return filepath
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error for {url}: {e}")
        except Exception as e:
            print(f"✗ An error occurred with {url}: {e}")
            
        return None
    
    def main(self):
        self.print_welcome()
        
        # Create directory if it doesn't exist
        try:
            os.makedirs("Fetched_Images", exist_ok=True)
        except OSError as e:
            print(f"✗ Cannot create directory: {e}")
            return
            
        # Get URLs from user
        urls = self.get_user_urls()
        if not urls:
            print("No URLs provided. Exiting.")
            return
            
        # Process each URL
        success_count = 0
        for url in urls:
            if self.download_image(url):
                success_count += 1
                
        # Print summary
        print("\n" + "="*50)
        print(f"Download completed. {success_count} of {len(urls)} images fetched successfully.")
        if success_count > 0:
            print("Connection strengthened. Community enriched.")
        print("Thank you for practicing Ubuntu.")

if __name__ == "__main__":
    fetcher = UbuntuImageFetcher()
    fetcher.main()