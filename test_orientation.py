import fitz
import io
import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def create_portrait_pdf():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842) # A4 Portrait
    page.insert_text((50, 50), "Portrait Page", fontsize=20)
    page.draw_rect((100, 100, 200, 200), color=(1,0,0), fill=(1,0,0)) # Red box
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def create_landscape_pdf():
    doc = fitz.open()
    page = doc.new_page(width=842, height=595) # A4 Landscape
    page.insert_text((50, 50), "Landscape Page", fontsize=20)
    page.draw_rect((100, 100, 200, 200), color=(1,0,0), fill=(1,0,0)) # Red box
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def test_orientation_logic():
    print("Testing Portrait PDF...")
    p_pdf = create_portrait_pdf()
    files = {'file': ('portrait.pdf', p_pdf, 'application/pdf')}
    response = client.post("/invert", files=files)
    if response.status_code == 200:
        with open("result_portrait.pdf", "wb") as f:
            f.write(response.content)
        print("Saved result_portrait.pdf (Should be partial invert)")
        
        try:
            doc = fitz.open("result_portrait.pdf")
            page = doc[0] # Keep page alive
            rect = page.rect
            annots = list(page.annots())
            if annots:
                annot = annots[0]
                print(f"Found annotation: {annot}")
                annot_rect = annot.rect
                height_ratio = annot_rect.height / rect.height
                print(f"Portrait Inversion Ratio: {height_ratio:.4f} (Expected ~0.435)")
            else:
                print("ERROR: No annotation found in portrait result")
                
        except Exception as e:
            print(f"Error inspecting output PDF: {e}")
    else:
        print("Portrait request failed")

    print("\nTesting Landscape PDF...")
    try:
        l_pdf = create_landscape_pdf()
        files = {'file': ('landscape.pdf', l_pdf, 'application/pdf')}
        response = client.post("/invert", files=files)
        if response.status_code == 200:
            with open("result_landscape.pdf", "wb") as f:
                f.write(response.content)
            print("Saved result_landscape.pdf (Should be FULL invert)")
            
            doc = fitz.open("result_landscape.pdf")
            page = doc[0] # Keep page alive
            rect = page.rect
            annots = list(page.annots())
            if annots:
                annot = annots[0]
                print(f"Found annotation: {annot}")
                annot_rect = annot.rect
                height_ratio = annot_rect.height / rect.height
                print(f"Landscape Inversion Ratio: {height_ratio:.4f} (Expected 1.0)")
            else:
                print("ERROR: No annotation found in landscape result")
    except Exception as e:
        print(f"Error inspecting output PDF: {e}")

if __name__ == "__main__":
    test_orientation_logic()
