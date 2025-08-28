#!/usr/bin/env python3
"""
Test script to debug yt-dlp issues
"""

import yt_dlp
import json

def test_yt_dlp():
    """Test yt-dlp functionality"""
    
    # Test URL
    url = "https://www.youtube.com/watch?v=9bZkp7q19f0"
    
    # Basic options
    ydl_opts = {
        'format': 'best',
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'ignoreerrors': False,
    }
    
    try:
        print(f"Testing yt-dlp with URL: {url}")
        print(f"yt-dlp version: {yt_dlp.version.__version__}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Extracting video info...")
            info = ydl.extract_info(url, download=False)
            
            print("Success! Video info extracted:")
            print(f"Title: {info.get('title', 'Unknown')}")
            print(f"Duration: {info.get('duration', 'Unknown')}")
            print(f"Uploader: {info.get('uploader', 'Unknown')}")
            
            # Check available formats
            if 'formats' in info:
                print(f"\nAvailable formats: {len(info['formats'])}")
                for fmt in info['formats'][:5]:  # Show first 5 formats
                    print(f"  - {fmt.get('format_id', 'N/A')}: {fmt.get('ext', 'N/A')} {fmt.get('height', 'N/A')}p")
            
            return True
            
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    success = test_yt_dlp()
    print(f"\nTest {'PASSED' if success else 'FAILED'}") 