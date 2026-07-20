# ══════════════════════════════════════════════════════════════
# BLOCK 10.5 — Zip the best adapter for download
# ══════════════════════════════════════════════════════════════
import shutil, os

ZIP_OUTPUT_DIR = "xxxxxxxxxx"

# create a zip of the best adapter folder
zip_base = f"{ZIP_OUTPUT_DIR}/best_adapter_{MODEL_TAG}"
shutil.make_archive(zip_base, 'zip', BEST_DIR)

zip_path = f"{zip_base}.zip"
size_mb = os.path.getsize(zip_path) / (1024 * 1024)
print(f"Zipped best adapter -> {zip_path}  ({size_mb:.1f} MB)")

# list what's inside so you can verify
print("\nContents:")
for f in os.listdir(BEST_DIR):
    fp = os.path.join(BEST_DIR, f)
    print(f"   {f}  ({os.path.getsize(fp)/1024:.0f} KB)")
