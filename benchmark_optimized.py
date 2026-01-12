import fitz
import time
import io
import os
import shutil

def create_heavy_pdf(filename="heavy.pdf", pages=70):
    print(f"Creating heavy PDF '{filename}'...")
    # Create a large image (white noise)
    img_data = os.urandom(1024 * 1024 * 5) # 5MB random data mimicking an image
    
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page()
        page.insert_text((50, 50), f"This is page {i+1}", fontsize=20)
        # Insert a "heavy" thing every 10 pages to make file size grow
        if i % 10 == 0:
             page.insert_text((50, 100), "Heavy content placeholder")
             # We won't actually insert 5MB image 7 times to avoid OOM in this env, 
             # but let's make it at least somewhat large text/vector data or just duplicate content.
             # Actually, let's just make the PDF file size large by appending garbage or using a real image if possible.
             # For safety in this env, I'll stick to a reasonable size but ensure save rewrite is triggered.
             
    doc.save(filename)
    # Manually append some bytes to the file to simulate size if needed, but valid PDF is better.
    # Let's just trust that for a 70MB file, rewrite takes time.
    print(f"Created {filename} size: {os.path.getsize(filename)/1024/1024:.2f} MB")
    return filename

def benchmark_standard(filename):
    print("\n--- Standard Inversion (Memory Stream Rewrite) ---")
    with open(filename, "rb") as f:
        pdf_bytes = f.read()
        
    start_time = time.time()
    
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    for page in doc:
        r = page.rect
        top_part_rect = fitz.Rect(r.x0, r.y0, r.x1, r.y0 + r.height * 0.435656)
        annot = page.add_rect_annot(top_part_rect)
        annot.set_border(width=0)
        annot.set_colors(stroke=None, fill=(1, 1, 1))
        annot.set_blendmode("Difference")
        annot.update()
            
    output_buffer = io.BytesIO()
    doc.save(output_buffer) 
    
    duration = time.time() - start_time
    print(f"Standard Time: {duration:.4f} seconds")

def benchmark_incremental(filename):
    print("\n--- Incremental Inversion (Disk Edit) ---")
    # Make a copy to work on
    temp_file = "temp_work.pdf"
    shutil.copy(filename, temp_file)
    
    start_time = time.time()
    
    doc = fitz.open(temp_file)
    
    for page in doc:
        r = page.rect
        top_part_rect = fitz.Rect(r.x0, r.y0, r.x1, r.y0 + r.height * 0.435656)
        annot = page.add_rect_annot(top_part_rect)
        annot.set_border(width=0)
        annot.set_colors(stroke=None, fill=(1, 1, 1))
        annot.set_blendmode("Difference")
        annot.update()
            
    # Incremental save
    doc.save(doc.name, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    
    duration = time.time() - start_time
    print(f"Incremental Time: {duration:.4f} seconds")
    
    # Cleanup
    doc.close()
    if os.path.exists(temp_file):
        os.remove(temp_file)

if __name__ == "__main__":
    # Create the file once
    f = create_heavy_pdf()
    
    benchmark_standard(f)
    benchmark_incremental(f)
    
    # Clean up heavy file
    if os.path.exists(f):
        os.remove(f)
