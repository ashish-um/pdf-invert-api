from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import io
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "status": "active"}

@app.post("/invert")
async def invert_pdf(file: UploadFile = File(...)):
    # Read the uploaded file
    file_content = await file.read()
    
    # Open the PDF
    doc = fitz.open(stream=file_content, filetype="pdf")
    
    # Process each page
    for page in doc:
        # Calculate the rectangle for the top some percentage of the page
        # specific to portrait (or any orientation really, "top" is 0-based Y usually)
        r = page.rect
        top_part_rect = fitz.Rect(r.x0, r.y0, r.x1, r.y0 + r.height * 0.435656)

        # Create a rectangle annotation covering the top part
        annot = page.add_rect_annot(top_part_rect)
        
        # Remove border
        annot.set_border(width=0)
        
        # Set fill color to white (1, 1, 1) and no stroke
        annot.set_colors(stroke=None, fill=(1, 1, 1))
        
        # Set blend mode to 'Difference' to invert colors
        annot.set_blendmode("Difference")
        
        # Update the annotation to apply changes
        annot.update()
    
    # Save the modified PDF to a bytes buffer
    output_buffer = io.BytesIO()
    doc.save(output_buffer)
    output_buffer.seek(0)
    
    # Return the file as a response
    return StreamingResponse(
        output_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=inverted.pdf"}
    )