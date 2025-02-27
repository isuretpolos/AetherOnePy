import os
import sqlite3
import sys
from typing import List
from datetime import datetime
import json

from flask import jsonify

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domains.aetherOneDomains import Case, Session, MapDesign, Feature, Analysis, Catalog, Rate, AnalysisRate, BroadCastData


class CaseDAO:
    def __init__(self, db_filename):
        self.conn = sqlite3.connect(db_filename, isolation_level=None, timeout=10, check_same_thread=False)
        self.conn.execute('PRAGMA journal_mode = WAL;')
        self.conn.execute('PRAGMA foreign_keys = ON;')
        self.create_table()

    def close(self):
        self.conn.close()

    def create_table(self):
        catalog_query = '''
        CREATE TABLE IF NOT EXISTS catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            author TEXT,
            importdate DATETIME
        )
        '''
        rate_query = '''
        CREATE TABLE IF NOT EXISTS rate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signature TEXT,
            description TEXT,
            catalog_id INTEGER NOT NULL
        )
        '''
        case_query = '''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            color TEXT,
            description TEXT,
            created DATETIME,
            last_change DATETIME
        )
        '''
        session_query = '''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intention TEXT,
            description TEXT,
            created DATETIME,
            case_id INTEGER,
            FOREIGN KEY (case_id) REFERENCES cases (id) ON DELETE CASCADE
        )
        '''
        broadcast_query = '''
        CREATE TABLE IF NOT EXISTS broadcast (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clear BOOLEAN,
            intention TEXT,
            signature TEXT,
            delay INTEGER,
            repeat INTEGER,
            analysis_id INTEGER,
            entering_with_general_vitality INTEGER,
            leaving_with_general_vitality INTEGER,
            session_id INTEGER,
            created DATETIME,
            FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
        )
        '''
        ## Here we need a sophisticated rate database
        analysis_object_query = '''
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note TEXT,
            target_gv INTEGER,
            session_id INTEGER,
            catalogId INTEGER,
            created DATETIME,
            FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
        )
        '''
        rate_for_analysis_query = '''
        CREATE TABLE IF NOT EXISTS rate_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signature TEXT,
            description TEXT,
            catalog_id INTEGER NOT NULL,
            analysis_id INTEGER NOT NULL,
            energetic_value INTEGER,
            gv INTEGER,
            level INTEGER,
            potencyType TEXT,
            potency INTEGER,
            note TEXT
        )
        '''
        map_design_query = '''
        CREATE TABLE IF NOT EXISTS map_design (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT,
            coordinates_x INTEGER,
            coordinates_y INTEGER,
            zoom INTEGER,
            feature_list TEXT
        )
        '''
        feature_query = '''
        CREATE TABLE IF NOT EXISTS feature (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            territory_name TEXT,
            simple_feature_data TEXT,
            simple_feature_type TEXT,
            note TEXT,
            url TEXT,
            last_update TEXT
        )
        '''
        self.conn.execute(catalog_query)
        self.conn.execute(rate_query)
        self.conn.execute(case_query)
        self.conn.execute(session_query)
        self.conn.execute(broadcast_query)
        self.conn.execute(analysis_object_query)
        self.conn.execute(rate_for_analysis_query)
        self.conn.execute(map_design_query)
        self.conn.execute(feature_query)
        self.conn.commit()

    def insert_catalog(self, catalog: Catalog):
        query = '''
        INSERT INTO catalog (name, description, author, importdate)
        VALUES (?, ?, ?, datetime('now'))
        '''
        self.conn.execute(query, (catalog.name, catalog.description, catalog.author))
        self.conn.commit()

    def get_catalog(self, catalog_id: int) -> Catalog | None:
        row = self.conn.execute('SELECT * FROM catalog WHERE id = ?', (catalog_id,)).fetchone()
        if row:
            catalog = Catalog(row[1], row[2], row[3], datetime.fromisoformat(row[4]))
            catalog.id = row[0]
            return catalog
        return None

    def get_catalog_by_name(self, name: str) -> Catalog | None:
        row = self.conn.execute('SELECT * FROM catalog WHERE name = ?', (name,)).fetchone()
        if row:
            catalog = Catalog(row[1], row[2], row[3], datetime.fromisoformat(row[4]))
            catalog.id = row[0]
            return catalog
        return None

    def delete_catalog(self, catalog_id: int):
        query = 'DELETE FROM catalog WHERE id = ?'
        self.conn.execute(query, (catalog_id,))
        self.conn.commit()

    def list_catalogs(self) -> List[Catalog]:
        cursor = self.conn.execute('SELECT * FROM catalog')
        catalogs = []
        for row in cursor:
            catalog = Catalog(row[1], row[2], row[3], datetime.fromisoformat(row[4]))
            catalog.id = row[0]
            catalogs.append(catalog)
        return catalogs

    def insert_rate(self, rate: Rate):
        query = '''
        INSERT INTO rate (signature, description, catalog_id)
        VALUES (?, ?, ?)
        '''
        self.conn.execute(query, (rate.signature, rate.description, rate.catalogID))
        self.conn.commit()

    def get_rate(self, rate_id: int) -> Rate | None:
        row = self.conn.execute('SELECT * FROM rate WHERE id = ?', (rate_id,)).fetchone()
        if row:
            rate = Rate(row[1], row[2], row[3])
            rate.id = row[0]
            return rate
        return None

    def delete_rate(self, rate_id: int):
        query = 'DELETE FROM rate WHERE id = ?'
        self.conn.execute(query, (rate_id,))
        self.conn.commit()

    def list_rates_from_catalog(self, catalog_id: int) -> List[Rate]:
        cursor = self.conn.execute('SELECT * FROM rate WHERE catalog_id = ?', (catalog_id,))
        rates = []
        for row in cursor:
            rate = Rate(row[1], row[2], row[3])
            rate.id = row[0]
            rates.append(rate)
        return rates

    def insert_case(self, case: Case):
        query = '''
        INSERT INTO cases (name, email, color, description, created, last_change)
        VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        '''
        cursor = self.conn.cursor() 
        cursor.execute(query, (case.name, case.email, case.color, case.description))
        self.conn.commit()

        # Get the last inserted ID
        last_id = cursor.lastrowid
        return last_id

    def get_case(self, case_id: int) -> Case | None:
        row = self.conn.execute('SELECT * FROM cases WHERE id = ?', (case_id,)).fetchone()
        if row:
            caseObj = Case(row[1], row[2], row[3], row[4],
                           datetime.fromisoformat(row[5]), datetime.fromisoformat(row[6]))
            caseObj.id = row[0]
            return caseObj
        return None

    def update_case(self, case: Case):
        query = '''
        UPDATE cases
        SET name = ?, email = ?, color = ?, description = ?, last_change = datetime('now')
        WHERE id = ?
        '''
        self.conn.execute(query, (case.name, case.email, case.color, case.description, case.id))
        self.conn.commit()

    def delete_case(self, case_id: int):
        query = 'DELETE FROM cases WHERE id = ?'
        self.conn.execute(query, (case_id,))
        self.conn.commit()

    def list_cases(self) -> List[Case]:
        query = 'SELECT * FROM cases'
        cursor = self.conn.execute(query)
        cases = []
        for row in cursor:
            caseObj = Case(row[1], row[2], row[3], row[4], datetime.fromisoformat(row[5]),
                           datetime.fromisoformat(row[6]))
            caseObj.id = row[0]
            cases.append(caseObj)
        return cases

    def insert_session(self, session: Session):
        query = '''
        INSERT INTO sessions (intention, description, created, case_id)
        VALUES (?, ?, datetime('now'), ?)
        '''
        cursor = self.conn.cursor()
        cursor.execute(query, (session.intention, session.description, session.caseID))
        session.id = cursor.lastrowid
        self.conn.commit()

    def get_session(self, session_id: int) -> Session:
        query = 'SELECT * FROM sessions WHERE id = ?'
        cursor = self.conn.execute(query, (session_id,))
        row = cursor.fetchone()
        if row:
            sessionObj = Session(row[1], row[2], row[4])
            sessionObj.created = datetime.fromisoformat(row[3])
            sessionObj.id = row[0]
            return sessionObj
        return None

    def get_last_session(self, case_id: int) -> Session:
        query = 'SELECT * FROM sessions WHERE case_id = ? ORDER BY created DESC, id DESC LIMIT 1'
        cursor = self.conn.execute(query, (case_id,))
        row = cursor.fetchone()
        if row:
            sessionObj = Session(row[1], row[2], row[4])
            sessionObj.created = datetime.fromisoformat(row[3])
            sessionObj.id = row[0]
            return sessionObj
        return None

    def delete_session(self, session_id: int):
        query = 'DELETE FROM sessions WHERE id = ?'
        self.conn.execute(query, (session_id,))
        self.conn.commit()

    def list_sessions(self, case_id: int) -> List[Session]:
        query = 'SELECT * FROM sessions WHERE case_id = ? ORDER BY id DESC'
        cursor = self.conn.execute(query, (case_id,))
        sessions = []
        for row in cursor:
            sessionObj = Session(row[1], row[2], case_id)
            sessionObj.id = row[0]
            sessionObj.created = datetime.fromisoformat(row[3])
            sessions.append(sessionObj)
        return sessions

    def insert_analysis(self, analysis: Analysis):
        query = '''
        INSERT INTO analysis (note, target_gv, session_id, catalogId, created)
        VALUES (?, ?, ?, ?, datetime('now'))
        '''
        cursor = self.conn.cursor()
        cursor.execute(query, (analysis.note, analysis.target_gv, analysis.sessionID, analysis.catalogId))
        analysis.id = cursor.lastrowid
        self.conn.commit()
        return analysis

    def get_analysis(self, analysis_id: int) -> Analysis | None:
        query = 'SELECT * FROM analysis WHERE id = ?'
        cursor = self.conn.execute(query, (analysis_id,))
        row = cursor.fetchone()
        if row:
            analysis = Analysis(row[1], row[3])
            analysis.id = row[0]
            analysis.target_gv = row[2]
            analysis.catalogId = row[4]
            analysis.created = datetime.fromisoformat(row[5])
            return analysis
        return None

    def get_last_analysis(self, session_id: int) -> Analysis | None:
        query = 'SELECT * FROM analysis WHERE session_id = ? ORDER BY created DESC, id DESC LIMIT 1'
        cursor = self.conn.execute(query, (session_id,))
        row = cursor.fetchone()
        if row:
            analysis = Analysis(row[1], row[3])
            analysis.id = row[0]
            analysis.target_gv = row[2]
            analysis.catalogId = row[4]
            analysis.created = datetime.fromisoformat(row[5])
            return analysis
        return None

    def update_analysis(self, analysis: Analysis):
        query = '''
        UPDATE analysis
        SET note = ?, target_gv = ?
        WHERE id = ?
        '''
        self.conn.execute(query, (analysis.note, analysis.target_gv, analysis.id))
        self.conn.commit()

    def delete_analysis(self, analysis_id: int):
        query = 'DELETE FROM analysis WHERE id = ?'
        self.conn.execute(query, (analysis_id,))
        self.conn.commit()

    def list_analysis(self, session_id: int) -> List[Analysis]:
        query = 'SELECT * FROM analysis WHERE session_id = ?'
        cursor = self.conn.execute(query, (session_id,))
        analysisList = []
        for row in cursor:
            analysis = Analysis(row[1], row[3])
            analysis.id = row[0]
            analysis.target_gv = row[2]
            analysis.catalogId = row[4]
            analysis.created = datetime.fromisoformat(row[5])
            analysisList.append(analysis)
        return analysisList

    def insert_rates_for_analysis(self, rates: List[AnalysisRate]):
        query = '''
        INSERT INTO rate_analysis (signature, description, catalog_id, analysis_id, energetic_value, gv, level, 
        potencyType, potency, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        '''
        rate_tuples = [rate.to_tuple() for rate in rates]
        self.conn.executemany(query, rate_tuples)
        self.conn.commit()

    def list_rates_for_analysis(self, analysis_id: int) -> List[AnalysisRate]:
        query = 'SELECT * FROM rate_analysis WHERE analysis_id = ?'
        cursor = self.conn.execute(query, (analysis_id,))
        rates = []
        for row in cursor:
            rate = AnalysisRate(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])
            rate.id = row[0]
            rates.append(rate)
        return rates
    
    def insert_broadcast(self, broadcast: BroadCastData):
        print(broadcast)
        query = '''
        INSERT INTO broadcast (clear, intention, signature, delay, repeat, analysis_id, entering_with_general_vitality,
        leaving_with_general_vitality, session_id, created)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        '''
        self.conn.execute(query, (broadcast.clear, broadcast.intention, broadcast.signature, broadcast.delay,
                                  broadcast.repeat, broadcast.analysis_id, broadcast.entering_with_general_vitality,
                                  broadcast.leaving_with_general_vitality, broadcast.sessionID))
        self.conn.commit()

    def insert_map_design(self, map_design: MapDesign):
        query = '''
        INSERT INTO map_design (uuid, coordinates_x, coordinates_y, zoom, feature_list)
        VALUES (?, ?, ?, ?, ?)
        '''
        self.conn.execute(query, (map_design.uuid, map_design.coordinates_x, map_design.coordinates_y,
                                  map_design.zoom, map_design.feature_list))
        self.conn.commit()

    def get_map_design(self, map_design_id: int) -> MapDesign:
        query = 'SELECT * FROM map_design WHERE id = ?'
        cursor = self.conn.execute(query, (map_design_id,))
        row = cursor.fetchone()
        if row:
            return MapDesign(row[1], row[2], row[3], row[4], json.loads(row[5]))
        return None

    def update_map_design(self, map_design_id: int, map_design: MapDesign):
        query = '''
        UPDATE map_design
        SET uuid = ?, coordinates_x = ?, coordinates_y = ?, zoom = ?, feature_list = ?
        WHERE id = ?
        '''
        self.conn.execute(query, (map_design.uuid, map_design.coordinates_x, map_design.coordinates_y,
                                  map_design.zoom, map_design.feature_list, map_design_id))
        self.conn.commit()

    def delete_map_design(self, map_design_id: int):
        query = 'DELETE FROM map_design WHERE id = ?'
        self.conn.execute(query, (map_design_id,))
        self.conn.commit()

    def list_map_designs(self) -> List[MapDesign]:
        query = 'SELECT * FROM map_design'
        cursor = self.conn.execute(query)
        map_designs = []
        for row in cursor:
            map_designs.append(MapDesign(row[1], row[2], row[3], row[4], json.loads(row[5])))
        return map_designs

    def insert_feature(self, feature: Feature):
        query = '''
        INSERT INTO feature (territory_name, simple_feature_data, simple_feature_type, note, url, last_update)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        self.conn.execute(query, (feature.territory_name, feature.simple_feature_data, feature.simple_feature_type,
                                  feature.note, feature.url, feature.last_update.isoformat()))
        self.conn.commit()

    def get_feature(self, feature_id: int) -> Feature:
        query = 'SELECT * FROM feature WHERE id = ?'
        cursor = self.conn.execute(query, (feature_id,))
        row = cursor.fetchone()
        if row:
            return Feature(row[1], row[2], row[3], row[4], row[5], datetime.fromisoformat(row[6]))
        return None

    def update_feature(self, feature_id: int, feature: Feature):
        query = '''
        UPDATE feature
        SET territory_name = ?, simple_feature_data = ?, simple_feature_type = ?, note = ?, url = ?, last_update = ?
        WHERE id = ?
        '''
        self.conn.execute(query, (feature.territory_name, feature.simple_feature_data, feature.simple_feature_type,
                                  feature.note, feature.url, feature.last_update.isoformat(), feature_id))
        self.conn.commit()

    def delete_feature(self, feature_id: int):
        query = 'DELETE FROM feature WHERE id = ?'
        self.conn.execute(query, (feature_id,))
        self.conn.commit()

    def list_features(self) -> List[Feature]:
        query = 'SELECT * FROM feature'
        cursor = self.conn.execute(query)
        features = []
        for row in cursor:
            features.append(Feature(row[1], row[2], row[3], row[4], row[5], datetime.fromisoformat(row[6])))
        return features

    def sqlSelect(self, sql:str):
        cursor = self.conn.execute(sql)
        # Get column names from cursor description
        column_names = [desc[0] for desc in cursor.description]
        # Fetch all rows as dictionaries
        rows = [dict(zip(column_names, row)) for row in cursor.fetchall()]
        # Prepare the final JSON structure
        result = {
            "sql": sql,
            "columns": column_names,
            "data": rows
        }
        return result

    def ensure_settings_defaults(self, settings: json):
        self.ensure_entry(settings,'hotbits_use_WebCam', False)
        self.ensure_entry(settings,'hotbits_use_Arduino', False)
        self.ensure_entry(settings,'hotbits_use_ESP', False)
        self.ensure_entry(settings,'hotbits_use_RPi', False)
        self.ensure_entry(settings,'hotbits_use_time_based_trng', True)
        self.ensure_entry(settings,'hotbits_collectAutomatically', False)
        self.ensure_entry(settings,'hotbits_mix_TRNG', False)
        self.ensure_entry(settings,'analysisAdvanced', False)
        self.ensure_entry(settings,'analysisAlwaysCheckGV', True)

    def getHotbitsSourcePriority(self):
        settings = self.loadSettings()
        prio = []
        if settings['hotbits_use_WebCam']:
            prio.append('WebCam')
        if settings['hotbits_use_Arduino']:
            prio.append('Arduino')
        if settings['hotbits_use_ESP']:
            prio.append('ESP')
        if settings['hotbits_use_RPi']:
            prio.append('RPi')
        if settings['hotbits_use_time_based_trng']:
            prio.append('TimeBaseTRNG')
        return prio


    def ensure_entry(self, dictionary, key, default_value):
        """
        Ensures that the key exists in the dictionary.
        If the key doesn't exist, it adds it with the default value.
        """
        if key not in dictionary:
            dictionary[key] = default_value

    def loadSettings(self) -> json:
        json_file_path = os.path.join(PROJECT_ROOT, "data", "settings.json")
        if os.path.isfile(json_file_path):
            with open(json_file_path, 'r') as f:
                settings = json.load(f)
                self.ensure_settings_defaults(settings)
                return settings
        else:
            with open(json_file_path, 'w') as f:
                settings = {'created': datetime.now().isoformat()}
                self.ensure_settings_defaults(settings)
                json.dump(settings, f)
            return jsonify(settings)

    def saveSettings(self, settings):
        json_file_path = os.path.join(PROJECT_ROOT, "data", "settings.json")
        self.ensure_settings_defaults(settings)
        with open(json_file_path, 'w') as f:
            json.dump(settings, f, indent=4)

    def get_setting(self, key:str):
        try:
            return self.loadSettings()[key]
        except:
            return None

    def __del__(self):
        self.conn.close()


# DAO Service to be imported into another class
def get_case_dao(db_filename: str) -> CaseDAO:
    return CaseDAO(db_filename)
