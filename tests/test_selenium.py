"""
Test Selenium Setup
Verify browser automation works
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_selenium():
    """Test basic Selenium functionality"""
    print("🧪 Testing Selenium Setup...\n")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without GUI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    print("1️⃣ Installing ChromeDriver...")
    service = Service(ChromeDriverManager().install())
    
    print("2️⃣ Starting Chrome browser...")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print("3️⃣ Navigating to Google...")
    driver.get("https://www.google.com")
    
    print(f"4️⃣ Page title: {driver.title}")
    
    print("5️⃣ Closing browser...")
    driver.quit()
    
    print("\n" + "="*50)
    print("🎉 Selenium is working!")
    print("="*50)

if __name__ == "__main__":
    test_selenium()
