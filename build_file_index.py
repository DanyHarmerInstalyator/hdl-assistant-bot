# import os
# import json
# import re
# from bot.utils.yandex_disk_client import get_folder_contents

# INDEX_PATH = "data/cache/file_index.json"
# os.makedirs("data/cache", exist_ok=True)

# def normalize(s: str) -> str:
#     return re.sub(r"[^a-z0-9]", "", s.lower())

# def build_index(base_path: str):
#     print(f"🔍 Строю индекс файлов из: {base_path}")
#     all_files = []
#     stack = [base_path]
#     visited = set()

#     while stack:
#         current = stack.pop()
#         if current in visited:
#             continue
#         visited.add(current)
#         print(f"  Обрабатываю: {current}")

#         try:
#             items = get_folder_contents(current)
#         except Exception as e:
#             print(f"⚠️ Ошибка {current}: {e}")
#             continue

#         for item in items:
#             if item["type"] == "dir":
#                 full_path = f"{current.rstrip('/')}/{item['name']}"
#                 stack.append(full_path)
#             elif item["name"].lower().endswith(".pdf"):
#                 all_files.append({
#                     "name": item["name"],
#                     "path": f"{current.rstrip('/')}/{item['name']}",
#                     "norm_name": normalize(item["name"])
#                 })

#     with open(INDEX_PATH, "w", encoding="utf-8") as f:
#         json.dump(all_files, f, ensure_ascii=False, indent=2)
#     print(f"✅ Индекс сохранён: {len(all_files)} PDF")

# if __name__ == "__main__":
#     from dotenv import load_dotenv
#     load_dotenv()
#     base = os.getenv("YANDEX_DISK_FOLDER_PATH", "/")
#     build_index(base)

# build_file_index.py
import os
import json
from bot.utils.yandex_disk_client import search_in_file_index, get_folder_contents, normalize_with_synonyms 

INDEX_PATH = "data/cache/file_index.json"
os.makedirs("data/cache", exist_ok=True)

def build_index(base_path: str):
    print(f"🔍 Строю индекс файлов из: {base_path}")
    all_files = []
    stack = [base_path]
    visited = set()

    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)

        try:
            items = get_folder_contents(current)
        except Exception as e:
            print(f"⚠️ Ошибка {current}: {e}")
            continue

        for item in items:
            if item["type"] == "dir":
                full_path = f"{current.rstrip('/')}/{item['name']}"
                stack.append(full_path)
            elif item["name"].lower().endswith(".pdf"):
                filename = item["name"]
                # Удаляем .pdf для нормализации
                name_without_ext = filename.rsplit(".", 1)[0] if "." in filename else filename
                norm_name = normalize_with_synonyms(name_without_ext)

                all_files.append({
                    "name": filename,
                    "path": f"{current.rstrip('/')}/{filename}",
                    "norm_name": norm_name
                })

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(all_files, f, ensure_ascii=False, indent=2)
    print(f"✅ Индекс сохранён: {len(all_files)} PDF")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    base = os.getenv("YANDEX_DISK_FOLDER_PATH", "/")
    build_index(base)