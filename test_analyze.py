from fastapi.testclient import TestClient
from main import app
import fitz
import io
import os

client = TestClient(app)

def create_test_pdf():
    """Creates a simple PDF with some text for testing."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello World! This is a test PDF.", fontsize=20)
    doc.set_metadata({"title": "Test Document", "author": "Test Author"})
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def test_analyze_endpoint():
    # Use existing test.pdf if present
    if os.path.exists("test.pdf"):
        print("Using existing 'test.pdf'...")
        with open("test.pdf", "rb") as f:
            pdf_content = f.read()
    else:
        print("Creating dummy PDF...")
        pdf_content = create_test_pdf().getvalue()
    
    # Send request
    files = {'file': ('test_analyze.pdf', pdf_content, 'application/pdf')}
    response = client.post("/analyze", files=files)
    
    # Check response
    if response.status_code == 200:
        data = response.json()
        print("Success: Endpoint returned 200 OK")
        print("Response Data:", data)
        
        # specific check for keys
        required_keys = ["filename", "size_mb", "pages", "title", "author", "orientation"]
        if all(k in data for k in required_keys):
            print("Verified all required keys are present.")
            print(f"Detected Orientation: {data.get('orientation')}")
        else:
            print("Missing keys in response:", data)
            
    else:
        print(f"Failed: Status code {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_analyze_endpoint()
