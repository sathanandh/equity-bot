# fix_newlines.py
from pathlib import Path

files_to_fix = [
    "src/equity_bot.py",
    "src/utils/pdf_extractor.py",
    "src/utils/telegram_client.py"
]

for file_path in files_to_fix:
    file = Path(file_path)
    if not file.exists():
        print(f"⚠️ File not found: {file_path}")
        continue
    
    content = file.read_text(encoding="utf-8")
    
    # Fix common patterns (be careful with this)
    # This is a simplified fix - review manually after
    content = content.replace('"\n', '"\\n')
    content = content.replace('\n"', '\\n"')
    content = content.replace("'\n", "'\\n")
    content = content.replace("\n'", "\\n'")
    
    file.write_text(content, encoding="utf-8")
    print(f"✅ Fixed: {file_path}")

print("\n⚠️ IMPORTANT: Review changes manually before committing!")