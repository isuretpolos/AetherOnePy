import os, sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domains.aetherOneDomains import Case, Session, Analysis, Catalog, Rate
from services.databaseService import get_case_dao, Case

aetherOneDB = get_case_dao('../data/aetherone.db')
class RateImporter:
    def generate_folder_file_json(self, rootFolder):
        result = {"folders": {}}

        for dirpath, dirnames, filenames in os.walk(rootFolder):
            folder_name = os.path.basename(dirpath)
            txt_files = [f for f in filenames if f.endswith('.txt')]
            if txt_files:
                result["folders"][folder_name] = txt_files

        return json.dumps(result, indent=2)

    def import_file(self, root_folder, file_name):
        # Search for the file in subfolders
        file_path = None
        for dirpath, dirnames, filenames in os.walk(root_folder):
            if file_name in filenames:
                file_path = os.path.join(dirpath, file_name)
                break

        if not file_path:
            print(f"File '{file_name}' not found in '{root_folder}'.")
            return

        # Insert the catalog and process the file
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        catalog_name = os.path.splitext(file_name)[0]
        import_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert catalog
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO catalog (name, description, author, importdate)
                VALUES (?, ?, ?, ?)
            """, (catalog_name, None, None, import_date))
            catalog_id = cursor.lastrowid

            # Insert rates for each non-empty line
            for line in lines:
                line = line.strip()
                if line:  # Ignore empty lines
                    signature, *description = line.split(' ', 1)
                    description = description[0] if description else None
                    cursor.execute("""
                        INSERT INTO rate (signature, description, catalog_id)
                        VALUES (?, ?, ?)
                    """, (signature, description, catalog_id))

        print(f"File '{file_name}' imported successfully.")

if __name__ == '__main__':
    rateImporter = RateImporter()
    json_result = rateImporter.generate_folder_file_json('../../data/radionics-rates')
    print(json_result)
