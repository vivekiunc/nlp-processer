import argparse
import json
import os
import jiwer
from context import DEFAULT_LANGUAGE, transcribe

EVAL_DIRS = {
    "te": "/Users/vivekindlamuri/rag_system/sources/audio_samples/eval",
    "mr": "/Users/vivekindlamuri/rag_system/sources/audio_samples/eval_mr",
}


def run_eval(language: str = DEFAULT_LANGUAGE):
    eval_dir = EVAL_DIRS[language]
    manifest_path = os.path.join(eval_dir, "manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    rows = []
    for entry in manifest:
        audio_path = os.path.join(eval_dir, entry["file"])
        reference = entry["reference"]
        hypothesis = transcribe(audio_path, language).strip()
        sample_wer = jiwer.wer(reference, hypothesis)
        sample_cer = jiwer.cer(reference, hypothesis)
        rows.append({
            "file": entry["file"],
            "reference": reference,
            "hypothesis": hypothesis,
            "wer": sample_wer,
            "cer": sample_cer,
        })

    references = [r["reference"] for r in rows]
    hypotheses = [r["hypothesis"] for r in rows]
    corpus_wer = jiwer.wer(references, hypotheses)
    corpus_cer = jiwer.cer(references, hypotheses)

    return rows, corpus_wer, corpus_cer


def print_report(rows, corpus_wer, corpus_cer):
    print(f"{'file':<14} {'WER':>6} {'CER':>6}   reference -> hypothesis")
    print("-" * 100)
    for r in rows:
        match = "" if r["wer"] == 0 else "  <-- word-level mismatch"
        print(f"{r['file']:<14} {r['wer']*100:5.1f}% {r['cer']*100:5.1f}%   {r['reference']!r} -> {r['hypothesis']!r}{match}")

    print("-" * 100)
    exact_matches = sum(1 for r in rows if r["wer"] == 0)
    print(f"Samples: {len(rows)} | Exact word-level matches: {exact_matches}/{len(rows)}")
    print(f"Corpus-level WER: {corpus_wer*100:.2f}%")
    print(f"Corpus-level CER: {corpus_cer*100:.2f}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", choices=sorted(EVAL_DIRS), default=DEFAULT_LANGUAGE)
    args = parser.parse_args()

    rows, corpus_wer, corpus_cer = run_eval(args.language)
    print_report(rows, corpus_wer, corpus_cer)
