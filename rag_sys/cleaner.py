import pymupdf4llm
import re, json

sources = [
    {"path": "/Users/vivekindlamuri/rag_system/sources/data1_160years_nlp.pdf", "crop": None, "topic": "irrigation", "region": "Andhra Pradesh - Krishna & Godavari deltas", "language": "en", "source": "gds_kds_160_years_irrigation.pdf"},
    {"path": "sources/angrau.pdf", "crop": "stored-pulses", "topic": "pest-management", "region": "India", "language": "en", "source": "jorangrau_2026_54_2_piper_chaba_pest.pdf"},
    {"path": "sources/paddy-yields.pdf", "crop": "rice", "topic": "climate-impact", "region": "Andhra Pradesh", "language": "en", "source": "cwe_2023_18_1_ap_climate_paddy_yields_ceres.pdf"},
    {"path": "sources/paddy-book.pdf", "crop": "rice", "topic": "pest-management", "region": "Andhra Pradesh", "language": "te", "source": "angrau_vari_pest_disease_nutrient_management_2022.pdf"}
]

with open("/Users/vivekindlamuri/rag_system/knowledge/knowledge_base.jsonl", "w", encoding = 'utf-8') as f:
    for s in sources:
        pages_data = pymupdf4llm.to_markdown(
            doc = s["path"],
            page_chunks = True,
            header = False,
            footer = False
        )

        for page in pages_data:
            record = {
                "text": page["text"],                            
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