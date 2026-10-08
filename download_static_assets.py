import os
import requests
from pathlib import Path

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / 'static'

# Create directories
(STATIC_DIR / 'css').mkdir(parents=True, exist_ok=True)
(STATIC_DIR / 'js').mkdir(parents=True, exist_ok=True)
(STATIC_DIR / 'fonts').mkdir(parents=True, exist_ok=True)

# Files to download
ASSETS = {
    'css': [
        ('bootstrap.rtl.min.css', 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css'),
        ('bootstrap-icons.css', 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css'),
        ('leaflet.css', 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'),
        ('select2.min.css', 'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css'),
    ],
    'js': [
        ('jquery-3.7.1.min.js', 'https://code.jquery.com/jquery-3.7.1.min.js'),
        ('bootstrap.bundle.min.js', 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'),
        ('leaflet.js', 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'),
        ('select2.min.js', 'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js'),
    ],
}

def download_file(url, dest):
    """Download a file from URL to destination"""
    print(f"Downloading {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(dest, 'wb') as f:
            f.write(response.content)
        print(f"✓ Downloaded {dest.name}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {url}: {e}")
        return False

def main():
    print("Starting download of static assets...")
    print("=" * 60)

    success_count = 0
    total_count = 0

    for subdir, files in ASSETS.items():
        for filename, url in files:
            total_count += 1
            dest = STATIC_DIR / subdir / filename
            if download_file(url, dest):
                success_count += 1

    print("=" * 60)
    print(f"Downloaded {success_count}/{total_count} files successfully")

    if success_count == total_count:
        print("✓ All assets downloaded successfully!")
    else:
        print(f"⚠ Some assets failed to download. You may need internet for those.")

if __name__ == '__main__':
    main()
