"""
update_index.py — centrale CLI die alles opnieuw bouwt.
Gebruik: python update_index.py
"""

from src.build_data_js    import build_data_js
from src.build_phonetic_js import build_phonetic_js
from src.db.schema        import init_db


if __name__ == '__main__':
    print("=" * 55)
    print("  Papiaments Leeravontuur — update_index.py")
    print("=" * 55)

    print("\n🗄️  Database...")
    init_db()

    print("\n📦 Data.js bouwen...")
    build_data_js()

    print("\n🔤 Phonetic.js bouwen...")
    build_phonetic_js()

    print("\n✅ Alles bijgewerkt. Push naar GitHub:")
    print("   git add docs/ update_index.py")
    print("   git commit -m 'Data bijgewerkt'")
    print("   git push")
