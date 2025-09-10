import os
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from io import BytesIO

# 📊 Fixed log file path
log_file = r"/content/drive/MyDrive/WATERMARKED/watermark_log.xlsx"

# 🔢 Start sequence
start_number = 100000

# Load existing log if available
if os.path.exists(log_file):
    df = pd.read_excel(log_file)
    if not df.empty:
        last_number = df.iloc[-1, 1]
        current_number = last_number + 1
    else:
        current_number = start_number
else:
    df = pd.DataFrame(columns=["File Path", "Watermark Number"])
    current_number = start_number

# 📷 Local image paths
search_img_path = r"/content/drive/MyDrive/WATERMARKED/search.png"
follow_img_path = r"/content/drive/MyDrive/WATERMARKED/follow.png"
whatsapp_img_path = r"/content/drive/MyDrive/WATERMARKED/whatsapp.png"

def create_overlay(page_width, page_height, text, number):
    """Create header + footer with aligned text and images"""
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    # --- Header ---
    header_height = 0.35 * inch
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, page_height - header_height, page_width, header_height, fill=1, stroke=0)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(0.4 * inch, page_height - 0.28 * inch,
                 "Not Official - mnopdf.com - WhatsApp - 9838225780")
    # --- Footer ---
    footer_height = 0.4 * inch
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, page_width, footer_height, fill=1, stroke=0)
    # Left-aligned text
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 9)
    c.drawString(0.35 * inch, 0.16 * inch, text)
    # --- Images aligned to right ---
    search_img = ImageReader(search_img_path)
    follow_img = ImageReader(follow_img_path)
    whatsapp_img = ImageReader(whatsapp_img_path)
    img_h = 0.25 * inch
    img_w_search = 0.8 * inch
    img_w_follow = 0.8 * inch
    img_w_whatsapp = 0.8 * inch
    margin_right = 0.4 * inch
    spacing = 0.1 * inch
    # Positioning right to left
    whatsapp_x = page_width - margin_right - img_w_whatsapp
    follow_x = whatsapp_x - spacing - img_w_follow
    search_x = follow_x - spacing - img_w_search
    img_y = 0.07 * inch
    # Draw search button
    c.drawImage(search_img, search_x, img_y, width=img_w_search, height=img_h, mask='auto')
    c.linkURL(f"https://www.mnopdf.com?search={number}",
              (search_x, img_y, search_x + img_w_search, img_y + img_h))
    # Draw follow button
    c.drawImage(follow_img, follow_x, img_y, width=img_w_follow, height=img_h, mask='auto')
    c.linkURL("https://www.instagram.com/vaikartana_raj/",
              (follow_x, img_y, follow_x + img_w_follow, img_y + img_h))
    # Draw whatsapp button
    c.drawImage(whatsapp_img, whatsapp_x, img_y, width=img_w_whatsapp, height=img_h, mask='auto')
    c.linkURL(f"https://wa.me/919838225780?text=I%20want%20help%20for%20PDF%20{number}",
              (whatsapp_x, img_y, whatsapp_x + img_w_whatsapp, img_y + img_h))
    c.save()
    packet.seek(0)
    return PdfReader(packet)

# 📂 Input folder
input_folder = r"/content/drive/MyDrive/OUTPUT1"

# Use os.walk to go through all folders and subfolders
for root, dirs, files in os.walk(input_folder):
    for filename in files:
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(root, filename)

            if pdf_path in df["File Path"].values:
                print(f"⚠️ Skipping already processed: {filename}")
                continue

            # Create the watermarked folder only if a PDF is found in the current directory
            output_folder = os.path.join(root, "watermarked")
            os.makedirs(output_folder, exist_ok=True)
            output_path = os.path.join(output_folder, filename)

            # Footer text with number
            footer_text = f"For Pdf solution Visit- mnopdf.com search - {current_number} , Query- Insta- Vaikartana_Raj"

            try:
                reader = PdfReader(pdf_path)
                writer = PdfWriter()

                for page in reader.pages:
                    page_width = float(page.mediabox.width)
                    page_height = float(page.mediabox.height)

                    # Create overlay
                    overlay_pdf = create_overlay(page_width, page_height, footer_text, current_number)
                    overlay_page = overlay_pdf.pages[0]

                    page.merge_page(overlay_page)
                    writer.add_page(page)

                # Save output
                with open(output_path, "wb") as f:
                    writer.write(f)

                # Log update
                df = pd.concat([df, pd.DataFrame([[pdf_path, current_number]], columns=df.columns)], ignore_index=True)
                df.to_excel(log_file, index=False)

                print(f"✅ Watermarked {filename} with number {current_number}")
                current_number += 1
            except Exception as e:
                print(f"❌ Could not process {filename}. Error: {e}")

print("🎉 All PDFs processed with header, footer, and WhatsApp button added!")