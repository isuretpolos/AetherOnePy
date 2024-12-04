import os
import sqlite3
import sys
from typing import List
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domains.aetherOneDomains import Case, Session, MapDesign, Feature, Analysis


class CaseDAO:
    def __init__(self, db_filename):
        self.conn = sqlite3.connect(db_filename, isolation_level=None, timeout=10, check_same_thread=False)
        self.conn.execute('PRAGMA journal_mode=WAL;')
        self.create_table()

    def close(self):
        self.conn.close()

    def create_table(self):
        case_query = '''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            color TEXT,
            description TEXT,
            created TEXT,
            last_change TEXT
        )
        '''
        session_query = '''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intention TEXT,
            description TEXT,
            created TEXT,
            analysis_result TEXT,
            broad_casted TEXT,
            case_id INTEGER,
            FOREIGN KEY (case_id) REFERENCES cases (id)
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
            entering_with_general_vitality INTEGER,
            leaving_with_general_vitality INTEGER,
            session_id INTEGER,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
        '''
        ## Here we need a sophisticated rate database
        analysis_object_query = '''
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note TEXT,
            session_id INTEGER,
            created DATETIME,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
        '''
        rate_object_query = '''
        CREATE TABLE IF NOT EXISTS "rate_object" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            occurrence INTEGER,
            overall_energetic_value INTEGER,
            overall_gv INTEGER,
            rate_object TEXT,
            name TEXT
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
        self.conn.execute(case_query)
        self.conn.execute(session_query)
        self.conn.execute(broadcast_query)
        self.conn.execute(analysis_object_query)
        self.conn.execute(rate_object_query)
        self.conn.execute(map_design_query)
        self.conn.execute(feature_query)
        self.conn.commit()

    def insert_case(self, case: Case):
        query = '''
        INSERT INTO cases (name, email, color, description, created, last_change)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        self.conn.execute(query, (case.name, case.email, case.color, case.description,
                                  case.created.isoformat(), case.last_change.isoformat()))
        self.conn.commit()

    def get_case(self, case_id: int) -> Case | None:
        row = self.conn.execute('SELECT * FROM cases WHERE id = ?', (case_id,)).fetchone()
        if row:
            return Case(row[1], row[2], row[3], row[4],
                        datetime.fromisoformat(row[5]), datetime.fromisoformat(row[6]))
        return None

    def get_all_cases(self) -> []:
        caseList = self.conn.execute('SELECT * FROM cases').fetchall()
        cases = []
        for row in caseList:
            cases.append(Case(row[1], row[2], row[3], row[4],
                              datetime.fromisoformat(row[5]), datetime.fromisoformat(row[6])))
        return cases

    def update_case(self, case_id: int, case: Case):
        query = '''
        UPDATE cases
        SET name = ?, email = ?, color = ?, description = ?, created = ?, last_change = ?
        WHERE id = ?
        '''
        self.conn.execute(query, (case.name, case.email, case.color, case.description,
                                  case.created.isoformat(), case.last_change.isoformat(), case_id))
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

    def insert_session(self, session: Session, case_id: int):
        query = '''
        INSERT INTO sessions (intention, description, created, case_id)
        VALUES (?, ?, ?, ?)
        '''
        self.conn.execute(query, (session.intention, session.description, session.created.isoformat(), case_id))
        self.conn.commit()

    def get_session(self, session_id: int) -> Session:
        query = 'SELECT * FROM sessions WHERE id = ?'
        cursor = self.conn.execute(query, (session_id,))
        row = cursor.fetchone()
        if row:
            return Session(row[1], row[2], datetime.fromisoformat(row[3]), json.loads(row[4]), json.loads(row[5]))
        return None

    def update_session(self, session_id: int, session: Session):
        query = '''
        UPDATE sessions
        SET intention = ?, description = ?, created = ?, analysis_result = ?, broad_casted = ?
        WHERE id = ?
        '''
        self.conn.execute(query, (session.intention, session.description, session.created.isoformat(),
                                  session.analysis_result, session.broad_casted, session_id))
        self.conn.commit()

    def delete_session(self, session_id: int):
        query = 'DELETE FROM sessions WHERE id = ?'
        self.conn.execute(query, (session_id,))
        self.conn.commit()

    def list_sessions(self, case_id: int) -> List[Session]:
        query = 'SELECT * FROM sessions WHERE case_id = ?'
        cursor = self.conn.execute(query, (case_id,))
        sessions = []
        for row in cursor:
            sessionObj = Session(row[1], row[2], datetime.fromisoformat(row[3]), case_id)
            sessionObj.id = row[0]
            sessions.append(sessionObj)
        return sessions

    def insert_analysis(self, analysis: Analysis, session_id: int):
        query = '''
        INSERT INTO analysis (note, session_id, created)
        VALUES (?, ?, DATETIME('now'))
        '''
        self.conn.execute(query, (analysis.note, session_id))
        self.conn.commit()

    def get_analysis(self, session_id: int) -> Session:
        query = 'SELECT * FROM analysis WHERE id = ?'
        cursor = self.conn.execute(query, (session_id,))
        row = cursor.fetchone()
        if row:
            return Session(row[1], row[2], datetime.fromisoformat(row[3]), json.loads(row[4]), json.loads(row[5]))
        return None

    def update_analysis(self, session_id: int, session: Session):
        query = '''
        UPDATE analysis
        SET intention = ?, description = ?, created = ?, analysis_result = ?, broad_casted = ?
        WHERE id = ?
        '''
        self.conn.execute(query, (session.intention, session.description, session.created.isoformat(),
                                  session.analysis_result, session.broad_casted, session_id))
        self.conn.commit()

    def delete_analysis(self, analysis_id: int):
        query = 'DELETE FROM analysis WHERE id = ?'
        self.conn.execute(query, (analysis_id,))
        self.conn.commit()

    def list_analysis(self, session_id: int) -> List[Session]:
        query = 'SELECT * FROM sessions WHERE case_id = ?'
        cursor = self.conn.execute(query, (session_id,))
        sessions = []
        for row in cursor:
            sessionObj = Session(row[1], row[2], datetime.fromisoformat(row[3]), session_id)
            sessionObj.id = row[0]
            sessions.append(sessionObj)
        return sessions

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

    def __del__(self):
        self.conn.close()


# DAO Service to be imported into another class
def get_case_dao(db_filename: str) -> CaseDAO:
    return CaseDAO(db_filename)