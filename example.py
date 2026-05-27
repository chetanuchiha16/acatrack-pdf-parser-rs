#!/usr/bin/env python3
"""
Example script demonstrating how to import and use the high-performance
native Rust PDF parsing engine (acatrack_rust) in Python.

Make sure you compile and install the extension into your current Python environment
before running this script:
    cd backend/acatrack_rust && maturin develop --release
"""

import os
import sys

try:
    import acatrack_rust
except ImportError:
    print("❌ Error: 'acatrack_rust' is not installed in the current environment.")
    print("Please compile and install it first using:")
    print("    cd backend/acatrack_rust && maturin develop --release")
    sys.exit(1)


def run_example():
    # 1. Define target subject codes to extract marks for
    target_subjects = [
        "BMATS101",  # Mathematics for CSE
        "BCHES102",  # Chemistry for CSE
        "BCEDK103",  # Computer-Aided Engineering Drawing
        "BENGK106",  # Professional Writing Skills in English
        "BICOK107",  # Constitution of India
        "BIDTK158",  # Innovation and Design Thinking
        "BPLCK105B", # Introduction to Python Programming
        "BESCK104C"  # Introduction to Electronics Engineering
    ]

    print("🚀 Initializing High-Performance Rust PDF Ingestion Engine...")
    print(f"📚 Subject Filter Set: {target_subjects}")
    print("=" * 70)

    # =========================================================================
    # ⚡ PART 1: Parse a Single PDF (Debugging / Telemetry Audit)
    # =========================================================================
    sample_pdf_path = "sample_result.pdf"

    if os.path.exists(sample_pdf_path):
        print(f"\n📂 [Part 1] Parsing Single PDF: {sample_pdf_path}")
        print("-" * 60)
        try:
            record = acatrack_rust.parse_single_pdf(
                pdf_path=sample_pdf_path,
                subject_codes=target_subjects
            )
            print("🏆 --- Extracted Student Details ---")
            print(f"👨‍🎓 USN  : {record.get('student_usn', 'NOT FOUND')}")
            print(f"👤 Name : {record.get('student_name', 'NOT FOUND')}")
            print(f"📅 Sem  : {record.get('SEMESTER', 'NOT FOUND')}")
            
            print("\n📚 --- Subject Marks ---")
            print(f"{'Subject Code':<15} | {'IA (Internal)':<13} | {'SEE (External)':<14}")
            print("-" * 50)
            for subject in sorted(target_subjects):
                ia = record.get(f"{subject}_INTERNALS")
                see = record.get(f"{subject}_EXTERNALS")
                print(f"{subject:<15} | {ia if ia is not None else 'N/A':<13} | {see if see is not None else 'N/A':<14}")

            print("\n📶 --- Native FFI Telemetry Logs ---")
            for log in record.get("logs", []):
                print(f"  [Rust] {log}")

        except Exception as e:
            print(f"❌ Error during single PDF parse: {e}")
    else:
        print(f"\nℹ️ [Part 1] Skipping single PDF demo (Create '{sample_pdf_path}' to test).")

    # =========================================================================
    # ⚡ PART 2: Rayon Parallel Batch Ingestion (Massive Throughput)
    # =========================================================================
    import time
    
    # Let's search the current directory for any provisional PDF results
    pdf_files = [f for f in os.listdir(".") if f.endswith(".pdf") and f != sample_pdf_path]
    
    # If no local PDFs, we'll create a list of mock paths to show how the parallel FFI is called
    if not pdf_files:
        print("\nℹ️ [Part 2] No extra PDFs found in the current directory.")
        print("Creating mock paths for demonstrating parallel FFI invocation...")
        pdf_paths = [f"mock_student_{i}.pdf" for i in range(1, 6)]
        is_mock = True
    else:
        pdf_paths = pdf_files
        is_mock = False

    print(f"\n📂 [Part 2] Rayon Multi-Threaded Batch Processing ({len(pdf_paths)} PDFs)...")
    print("-" * 60)
    
    start_time = time.perf_counter()
    try:
        # Call the native Rust Rayon parallel batch compiler!
        # This releases the Python GIL and saturates all available CPU threads!
        batch_records = acatrack_rust.parse_pdfs_parallel(
            pdf_paths=pdf_paths,
            subject_codes=target_subjects
        )
        duration = time.perf_counter() - start_time

        print(f"✅ Batch parsing completed in {duration:.4f} seconds!")
        if not is_mock:
            print(f"⚡ Throughput: {len(pdf_paths) / duration:.2f} PDFs/second")
        
        print(f"\n🏆 --- Batch Extraction Summary ({len(batch_records)} records processed) ---")
        print(f"{'Index':<5} | {'PDF Path':<25} | {'USN':<12} | {'Name':<20} | {'Marks Parsed':<12}")
        print("-" * 80)
        
        for idx, (path, record) in enumerate(zip(pdf_paths, batch_records)):
            if record:
                usn = record.get('student_usn') or "NOT FOUND"
                name = record.get('student_name') or "NOT FOUND"
                # Count how many subjects had successfully extracted marks
                extracted_count = sum(
                    1 for s in target_subjects 
                    if record.get(f"{s}_INTERNALS") is not None
                )
                print(f"{idx + 1:<5} | {path[:23]:<25} | {usn:<12} | {name[:18]:<20} | {extracted_count}/{len(target_subjects)}")
            else:
                print(f"{idx + 1:<5} | {path[:23]:<25} | ❌ PARSE FAILED / SKIPPED")

    except Exception as e:
        print(f"❌ Error during parallel batch parse: {e}")


if __name__ == "__main__":
    run_example()
