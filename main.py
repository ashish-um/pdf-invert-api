from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import io
import os
import uuid

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

@app.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        pages = len(doc)
        info = doc.metadata
        return {
            "filename": file.filename,
            "size_mb": round(size_mb, 2),
            "pages": pages,
            "title": info.get("title", ""),
            "author": info.get("author", "")
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/invert")
async def invert_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # Create a temporary file in the system temp directory
    # This ensures it works on read-only file systems (like some container setups)
    temp_filename = os.path.join(os.getcwd(), f"temp_{uuid.uuid4()}.pdf")
    # Ideally use proper temp dir, but let's stick to CWD if we want simple relative paths, 
    # OR use /tmp explicitly. Let's use tempfile.gettempdir() for best practice.
    import tempfile
    temp_filename = os.path.join(tempfile.gettempdir(), f"temp_{uuid.uuid4()}.pdf")
    
    # Write uploaded content to the temp file
    with open(temp_filename, "wb") as f:
        while content := await file.read(1024 * 1024):  # Read in chunks
            f.write(content)
            
    try:
        # Open the PDF from disk
        doc = fitz.open(temp_filename)
        
        # Process each page
        for page in doc:
            # Calculate the rectangle for the top some percentage of the page
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
        
        # Save incrementally to the same file (FAST!)
        doc.save(doc.name, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
        doc.close()
        
        # Callback to remove file after sending
        def cleanup():
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
        background_tasks.add_task(cleanup)

        # Return the file as a response
        return FileResponse(
            temp_filename,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=inverted.pdf"}
        )

    except Exception as e:
        # Cleanup on error
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        return {"error": str(e)}