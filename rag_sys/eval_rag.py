from retrieval import querier

# Each entry: a query and the source filename it should surface in the top-k results.
# Queries mix English and Telugu, including cross-lingual cases (Telugu query against an
# English-only document, and vice versa) to check the embedding model bridges languages.
LABELED_QUERIES = [
    # gds_kds_160_years_irrigation.pdf (EN, irrigation / Krishna & Godavari deltas)
    {"query": "History of irrigation development in Krishna and Godavari deltas", "expected_source": "gds_kds_160_years_irrigation.pdf"},
    {"query": "Inland water transport on rivers in Andhra Pradesh", "expected_source": "gds_kds_160_years_irrigation.pdf"},
    {"query": "కృష్ణా గోదావరి డెల్టాల్లో నీటిపారుదల చరిత్ర", "expected_source": "gds_kds_160_years_irrigation.pdf"},

    # jorangrau_2026_54_2_piper_chaba_pest.pdf (EN, stored-pulse pest management)
    {"query": "How to protect stored pulses from Callosobruchus chinensis beetle", "expected_source": "jorangrau_2026_54_2_piper_chaba_pest.pdf"},
    {"query": "Botanical pesticide for stored grain pests using Piper chaba plant", "expected_source": "jorangrau_2026_54_2_piper_chaba_pest.pdf"},
    {"query": "నిల్వ చేసిన పప్పుధాన్యాలలో పురుగుల నివారణ", "expected_source": "jorangrau_2026_54_2_piper_chaba_pest.pdf"},

    # cwe_2023_18_1_ap_climate_paddy_yields_ceres.pdf (EN, climate impact on paddy yield)
    {"query": "Impact of climate change on paddy rice yields in Andhra Pradesh", "expected_source": "cwe_2023_18_1_ap_climate_paddy_yields_ceres.pdf"},
    {"query": "CERES crop model simulation for rice yield prediction", "expected_source": "cwe_2023_18_1_ap_climate_paddy_yields_ceres.pdf"},
    {"query": "వాతావరణ మార్పు వరి దిగుబడిపై ప్రభావం", "expected_source": "cwe_2023_18_1_ap_climate_paddy_yields_ceres.pdf"},

    # angrau_vari_pest_disease_nutrient_management_2022.pdf (TE, rice pest/disease/nutrient bulletin)
    {"query": "వరి పంటలో ఆకుముడత తెగులు యాజమాన్యం", "expected_source": "angrau_vari_pest_disease_nutrient_management_2022.pdf"},
    {"query": "వరిలో పోషక లోపాల లక్షణాలు", "expected_source": "angrau_vari_pest_disease_nutrient_management_2022.pdf"},
    {"query": "Rice crop nutrient deficiency symptoms and management", "expected_source": "angrau_vari_pest_disease_nutrient_management_2022.pdf"},

    # apssdcl_paddy_varieties.pdf (EN, paddy seed varieties)
    {"query": "High yielding paddy seed varieties available in Andhra Pradesh", "expected_source": "apssdcl_paddy_varieties.pdf"},
    {"query": "Certified rice seed varieties for cultivation", "expected_source": "apssdcl_paddy_varieties.pdf"},

    # krishna_district_irrigation_profile.pdf (EN, Krishna district irrigation profile)
    {"query": "Irrigation profile of Krishna district canals", "expected_source": "krishna_district_irrigation_profile.pdf"},
    {"query": "Krishna district water resources for farming", "expected_source": "krishna_district_irrigation_profile.pdf"},
]

TOP_K = 3


def run_eval():
    rows = []
    for case in LABELED_QUERIES:
        results = querier(case["query"], top_k=TOP_K)
        sources = [r["source"] for r in results]
        rank = None
        for i, src in enumerate(sources, start=1):
            if src == case["expected_source"]:
                rank = i
                break
        rows.append({
            "query": case["query"],
            "expected_source": case["expected_source"],
            "retrieved_sources": sources,
            "rank": rank,
        })
    return rows


def print_report(rows):
    hits = sum(1 for r in rows if r["rank"] is not None)
    mrr = sum((1 / r["rank"]) for r in rows if r["rank"] is not None) / len(rows)

    for r in rows:
        status = f"HIT @ rank {r['rank']}" if r["rank"] else "MISS"
        print(f"[{status}] {r['query']!r}")
        print(f"    expected: {r['expected_source']}")
        print(f"    retrieved: {r['retrieved_sources']}")
        print()

    print("-" * 80)
    print(f"Queries: {len(rows)} | Hit@{TOP_K}: {hits}/{len(rows)} ({hits/len(rows)*100:.1f}%)")
    print(f"Mean Reciprocal Rank: {mrr:.3f}")


if __name__ == "__main__":
    rows = run_eval()
    print_report(rows)
