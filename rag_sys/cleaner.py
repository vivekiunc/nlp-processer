import io
import os
import pymupdf
import pymupdf4llm
import pytesseract
import re, json
from PIL import Image

sources = [
    {"path": "/Users/vivekindlamuri/rag_system/sources/data1_160years_nlp.pdf", "crop": None, "topic": "irrigation", "region": "Andhra Pradesh - Krishna & Godavari deltas", "language": "en", "source": "gds_kds_160_years_irrigation.pdf"},
    # angrau.pdf is a full journal issue (16 unrelated articles across plant sciences, social
    # sciences, home science, climate science, etc). Only pages 4-12 (0-indexed) are the
    # "Piper chaba" pest-management article these metadata tags actually describe; every other
    # page was previously getting mislabeled with this same crop/topic/source.
    {"path": "sources/angrau.pdf", "crop": "stored-pulses", "topic": "pest-management", "region": "India", "language": "en", "source": "jorangrau_2026_54_2_piper_chaba_pest.pdf", "page_range": (4, 13)},
    {"path": "sources/paddy-yields.pdf", "crop": "rice", "topic": "climate-impact", "region": "Andhra Pradesh", "language": "en", "source": "cwe_2023_18_1_ap_climate_paddy_yields_ceres.pdf"},
    # paddy-book.pdf uses a legacy, non-Unicode Telugu font with no ToUnicode CMap, so the normal
    # text layer extracts as garbage codepoints. OCR (reading the rendered glyphs as an image)
    # is required to get real Telugu Unicode text out of it.
    {"path": "sources/paddy-book.pdf", "crop": "rice", "topic": "pest-management", "region": "Andhra Pradesh", "language": "te", "source": "angrau_vari_pest_disease_nutrient_management_2022.pdf", "ocr": True}
]


def ocr_extract_pages(path, lang="tel", dpi=300):
    doc = pymupdf.open(path)
    file_name = os.path.basename(path)
    pages = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=dpi)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img, lang=lang)
        pages.append({"text": text, "metadata": {"page": i, "file_name": file_name}})
    return pages


with open("/Users/vivekindlamuri/rag_system/knowledge/knowledge_base.jsonl", "w", encoding = 'utf-8') as f:
    for s in sources:
        if s.get("ocr"):
            pages_data = ocr_extract_pages(s["path"])
        else:
            pages_data = pymupdf4llm.to_markdown(
                doc = s["path"],
                page_chunks = True,
                header = False,
                footer = False
            )

        start, end = s.get("page_range", (0, len(pages_data)))
        pages_data = pages_data[start:end]

        for page in pages_data:
            text = page["text"].strip()
            if not text:
                continue

            record = {
                "text": text,
                "page_number": page["metadata"].get("page"),
                "file_path": page["metadata"].get("file_name"),

                "crop": s["crop"],
                "region": s["region"],
                "language": s["language"],
                "source": s["source"],
                "topic" : s["topic"]
            }

            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        print(f"done processing and saving all pages for: {s['source']}")

sources = [
    {"path": "sources/apseeds.txt", "crop": "rice", "region": "Andhra Pradesh", "language": "en", "source": "apssdcl_paddy_varieties.pdf", "topic" : "seed_varieties"},
    {"path": "sources/irrigation_cycle.txt", "crop": None, "region": "Krishna district, Andhra Pradesh", "language": "en", "source": "krishna_district_irrigation_profile.pdf", "topic" : "irrigation"}
]

with open("/Users/vivekindlamuri/rag_system/knowledge/knowledge_base1.jsonl", "w", encoding="utf-8") as f:
    for s in sources:
        
        with open(s["path"], "r", encoding="utf-8") as txt_file:
            raw_content = txt_file.read()
        
        clean_content = raw_content.strip()
        

        text_chunks = clean_content.split("\n\n")
        
        for index, chunk in enumerate(text_chunks):
            if not chunk.strip():
                continue
                
            record = {
                "text": chunk.strip(),                           
                "chunk_id": index + 1,                           
                "file_path": s["path"],                          
                
                "crop": s["crop"],
                "region": s["region"],
                "language": s["language"],
                "source": s["source"],
                "topic": s["topic"]
            }
            
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            
        print(f"done processing and saving all chunks for: {s['source']}")