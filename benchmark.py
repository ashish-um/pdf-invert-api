import fitz
import time
import io

def create_large_pdf(pages=70):
    print(f"Creating {pages}-page dummy PDF...")
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page()
        page.insert_text((50, 50), f"This is page {i+1}", fontsize=20)
        # Add some shapes to make it slightly realistic
        page.draw_rect((100, 100, 400, 400), color=(0, 0, 1), fill=(0, 1, 0))
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer, doc

def benchmark_inversion(pdf_bytes):
    print("Starting inversion benchmark...")
    start_time = time.time()
    
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    for i, page in enumerate(doc):
        # Logic from main.py
        r = page.rect
        top_part_rect = fitz.Rect(r.x0, r.y0, r.x1, r.y0 + r.height * 0.435656)

        annot = page.add_rect_annot(top_part_rect)
        annot.set_border(width=0)
        annot.set_colors(stroke=None, fill=(1, 1, 1))
        annot.set_blendmode("Difference")
        annot.update()
        
        if (i + 1) % 10 == 0:
            print(f"Processed {i+1} pages...")
            
    output_buffer = io.BytesIO()
    # Using garbage=4 usually helps with size but check if it affects speed
    doc.save(output_buffer) 
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"Inversion complete. Time taken: {duration:.2f} seconds")

if __name__ == "__main__":
    pdf_bytes, _ = create_large_pdf(70)
    benchmark_inversion(pdf_bytes)
