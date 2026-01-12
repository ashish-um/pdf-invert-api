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
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def test_invert_endpoint():
    # Use existing test.pdf if present, otherwise create a dummy one
    if os.path.exists("test.pdf"):
        print("Using existing 'test.pdf'...")
        with open("test.pdf", "rb") as f:
            pdf_content = f.read()
    else:
        print("Creating dummy PDF...")
        pdf_content = create_test_pdf().getvalue()
    
    # Send request
    files = {'file': ('test.pdf', pdf_content, 'application/pdf')}
    response = client.post("/invert", files=files)
    
    # Check response
    if response.status_code == 200:
        print("Success: Endpoint returned 200 OK")
        
        # Save output to verify visually
        with open("inverted_test.pdf", "wb") as f:
            f.write(response.content)
        print("Saved inverted PDF to 'inverted_test.pdf'. Please check it visually.")
        
        # Basic check: is it a valid PDF?
        try:
            doc = fitz.open(stream=response.content, filetype="pdf")
            print(f"Verified output is a valid PDF with {len(doc)} pages.")
        except Exception as e:
            print(f"Error: Output is not a valid PDF. {e}")
            
    else:
        print(f"Failed: Status code {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    try:
        # Check if httpx is installed (required for TestClient)
        import httpx
        test_invert_endpoint()
    except ImportError:
        print("Please install 'httpx' to run this test: pip install httpx")
