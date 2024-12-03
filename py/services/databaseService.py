import sqlite3
from typing import List
from datetime import datetime
import json

# Define models based on the domain objects
class Case:
    def __init__(self, name: str, map_design: dict, email: str, color: str, description: str, created: datetime,
                 last_change: datetime, session_list: List[dict], top_ten_list: List[dict]):
        self.name = name
        self.map_design = json.dumps(map_design)
        self.email = email
        self.color = color
        self.description = description
        self.created = created
        self.last_change = last_change
        self.session_list = json.dumps(session_list)
        self.top_ten_list = json.dumps(top_ten_list)

class Session:
    def __init__(self, intenion: str, description: str, created: datetime, analysis_result: dict, broad_casted: dict):
        self.intenion = intenion
        self.description = description
        self.created = created
        self.analysis_result = json.dumps(analysis_result)
        self.broad_casted = json.dumps(broad_casted)

class BroadCastData:
    def __init__(self, clear: bool, intention: str, signature: str, delay: int, repeat: int,
                 entering_with_general_vitality: int, leaving_with_general_vitality: int):
        self.clear = clear
        self.intention = intention
        self.signature = signature
        self.delay = delay
        self.repeat = repeat
        self.entering_with_general_vitality = entering_with_general_vitality
        self.leaving_with_general_vitality = leaving_with_general_vitality

class RateObjectWrapper:
    def __init__(self, occurrence: int, overall_energetic_value: int, overall_gv: int, rate_object: dict, name: str):
        self.occurrence = occurrence
        self.overall_energetic_value = overall_energetic_value
        self.overall_gv = overall_gv
        self.rate_object = json.dumps(rate_object)
        self.name = name

class MapDesign:
    def __init__(self, uuid: str, coordinates_x: int, coordinates_y: int, zoom: int, feature_list: List[dict]):
        self.uuid = uuid
        self.coordinates_x = coordinates_x
        self.coordinates_y = coordinates_y
        self.zoom = zoom
        self.feature_list = json.dumps(feature_list)

class Feature:
    def __init__(self, territory_name: str, simple_feature_data: str, simple_feature_type: str, note: str, url: str,
                 last_update: datetime):
        self.territory_name = territory_name
        self.simple_feature_data = simple_feature_data
        self.simple_feature_type = simple_feature_type
        self.note = note
        self.url = url
        self.last_update = last_update

class CaseDAO:
    def __init__(self, db_filename):
        self.conn = sqlite3.connect(db_filename, isolation_level=None, timeout=10, check_same_thread=False)
        self.conn.execute('PRAGMA journal_mode=WAL;')
        self.create_table()

    def close(self):
        self.conn.close()

    def create_table(self):
        case_query = '''
        CREATE TABLE IF NOT EXISTS "case" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            map_design TEXT,
            email TEXT,
            color TEXT,
            description TEXT,
            created TEXT,
            last_change TEXT,
            session_list TEXT,
            top_ten_list TEXT
        )
        '''
        session_query = '''
        CREATE TABLE IF NOT EXISTS "session" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intenion TEXT,
            description TEXT,
            created TEXT,
            analysis_result TEXT,
            broad_casted TEXT,
            case_id INTEGER,
            FOREIGN KEY (case_id) REFERENCES "case" (id)
        )
        '''
        broadcast_query = '''
        CREATE TABLE IF NOT EXISTS "broadcast" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clear BOOLEAN,
            intention TEXT,
            signature TEXT,
            delay INTEGER,
            repeat INTEGER,
            entering_with_general_vitality INTEGER,
            leaving_with_general_vitality INTEGER
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
        CREATE TABLE IF NOT EXISTS "map_design" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT,
            coordinates_x INTEGER,
            coordinates_y INTEGER,
            zoom INTEGER,
            feature_list TEXT
        )
        '''
        feature_query = '''
        CREATE TABLE IF NOT EXISTS "feature" (
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
        self.conn.execute(rate_object_query)
        self.conn.execute(map_design_query)
        self.conn.execute(feature_query)
        self.conn.commit()

    def insert_case(self, case: Case):
        query = '''
        INSERT INTO "case" (name, map_design, email, color, description, created, last_change, session_list, top_ten_list)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.conn.execute(query, (case.name, case.map_design, case.email, case.color, case.description,
                                  case.created.isoformat(), case.last_change.isoformat(),
                                  case.session_list, case.top_ten_list))
        self.conn.commit()

    def get_case(self, case_id: int) -> Case:
        query = 'SELECT * FROM "case" WHERE id = ?'
        cursor = self.conn.execute(query, (case_id,))
        row = cursor.fetchone()
        if row:
            return Case(row[1], json.loads(row[2]), row[3], row[4], row[5],
                        datetime.fromisoformat(row[6]), datetime.fromisoformat(row[7]),
                        json.loads(row[8]), json.loads(row[9]))
        return None

    def update_case(self, case_id: int, case: Case):
        query = '''
        UPDATE "case"
        SET name = ?, map_design = ?, email = ?, color = ?, description = ?,
            created = ?, last_change = ?, session_list = ?, top_ten_list = ?
        WHERE id = ?
        '''
        self.conn.execute(query, (case.name, case.map_design, case.email, case.color, case.description,
                                  case.created.isoformat(), case.last_change.isoformat(),
                                  case.session_list, case.top_ten_list, case_id))
        self.conn.commit()

    def delete_case(self, case_id: int):
        query = 'DELETE FROM "case" WHERE id = ?'
        self.conn.execute(query, (case_id,))
        self.conn.commit()

    def list_cases(self) -> List[Case]:
        query = 'SELECT * FROM "case"'
        cursor = self.conn.execute(query)
        cases = []
        for row in cursor:
            cases.append(Case(row[1], json.loads(row[2]), row[3], row[4], row[5],
                              datetime.fromisoformat(row[6]), datetime.fromisoformat(row[7]),
                              json.loads(row[8]), json.loads(row[9])))
        return cases

    def insert_session(self, session: Session, case_id: int):
        query = '''
        INSERT INTO "session" (intenion, description, created, analysis_result, broad_casted, case_id)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        self.conn.execute(query, (session.intenion, session.description, session.created.isoformat(),
                                  session.analysis_result, session.broad_casted, case_id))
        self.conn.commit()

    def get_session(self, session_id: int) -> Session:
        query = 'SELECT * FROM "session" WHERE id = ?'
        cursor = self.conn.execute(query, (session_id,))
        row = cursor.fetchone()
        if row:
            return Session(row[1], row[2], datetime.fromisoformat(row[3]), json.loads(row[4]), json.loads(row[5]))
        return None

    def update_session(self, session_id: int, session: Session):
        query = '''
        UPDATE "session"
        SET intenion = ?, description = ?, created = ?, analysis_result = ?, broad_casted = ?
        WHERE id = ?
        '''
        self.conn.execute(query, (session.intenion, session.description, session.created.isoformat(),
                                  session.analysis_result, session.broad_casted, session_id))
        self.conn.commit()

    def delete_session(self, session_id: int):
        query = 'DELETE FROM "session" WHERE id = ?'
        self.conn.execute(query, (session_id,))
        self.conn.commit()

    def list_sessions(self, case_id: int) -> List[Session]:
        query = 'SELECT * FROM "session" WHERE case_id = ?'
        cursor = self.conn.execute(query, (case_id,))
        sessions = []
        for row in cursor:
            sessions.append(Session(row[1], row[2], datetime.fromisoformat(row[3]), json.loads(row[4]), json.loads(row[5])))
        return sessions

    def insert_rate_object(self, rate_object: RateObjectWrapper):
        query = '''
        INSERT INTO "rate_object" (occurrence, overall_energetic_value, overall_gv, rate_object, name)
        VALUES (?, ?, ?, ?, ?)
        '''
        self.conn.execute(query, (rate_object.occurrence, rate_object.overall_energetic_value, rate_object.overall_gv,
                                  rate_object.rate_object, rate_object.name))
        self.conn.commit()

    def get_rate_object(self, rate_object_id: int) -> RateObjectWrapper:
        query = 'SELECT * FROM "rate_object" WHERE id = ?'
        cursor = self.conn.execute(query, (rate_object_id,))
        row = cursor.fetchone()
        if row:
            return RateObjectWrapper(row[1], row[2], row[3], json.loads(row[4]), row[5])
        return None

    def update_rate_object(self, rate_object_id: int, rate_object: RateObjectWrapper):
        query = '''
        UPDATE "rate_object"
        SET occurrence = ?, overall_energetic_value = ?, overall_gv = ?, rate_object = ?, name = ?
        WHERE id = ?
        '''
        self.conn.execute(query, (rate_object.occurrence, rate_object.overall_energetic_value, rate_object.overall_gv,
                                  rate_object.rate_object, rate_object.name, rate_object_id))
        self.conn.commit()

    def delete_rate_object(self, rate_object_id: int):
        query = 'DELETE FROM "rate_object" WHERE id = ?'
        self.conn.execute(query, (rate_object_id,))
        self.conn.commit()

    def list_rate_objects(self) -> List[RateObjectWrapper]:
        query = 'SELECT * FROM "rate_object"'
        cursor = self.conn.execute(query)
        rate_objects = []
        for row in cursor:
            rate_objects.append(RateObjectWrapper(row[1], row[2], row[3], json.loads(row[4]), row[5]))
        return rate_objects

    def insert_map_design(self, map_design: MapDesign):
        query = '''
        INSERT INTO "map_design" (uuid, coordinates_x, coordinates_y, zoom, feature_list)
        VALUES (?, ?, ?, ?, ?)
        '''
        self.conn.execute(query, (map_design.uuid, map_design.coordinates_x, map_design.coordinates_y,
                                  map_design.zoom, map_design.feature_list))
        self.conn.commit()

    def get_map_design(self, map_design_id: int) -> MapDesign:
        query = 'SELECT * FROM "map_design" WHERE id = ?'
        cursor = self.conn.execute(query, (map_design_id,))
        row = cursor.fetchone()
        if row:
            return MapDesign(row[1], row[2], row[3], row[4], json.loads(row[5]))
        return None

    def update_map_design(self, map_design_id: int, map_design: MapDesign):
        query = '''
        UPDATE "map_design"
        SET uuid = ?, coordinates_x = ?, coordinates_y = ?, zoom = ?, feature_list = ?
        WHERE id = ?
        '''
        self.conn.execute(query, (map_design.uuid, map_design.coordinates_x, map_design.coordinates_y,
                                  map_design.zoom, map_design.feature_list, map_design_id))
        self.conn.commit()

    def delete_map_design(self, map_design_id: int):
        query = 'DELETE FROM "map_design" WHERE id = ?'
        self.conn.execute(query, (map_design_id,))
        self.conn.commit()

    def list_map_designs(self) -> List[MapDesign]:
        query = 'SELECT * FROM "map_design"'
        cursor = self.conn.execute(query)
        map_designs = []
        for row in cursor:
            map_designs.append(MapDesign(row[1], row[2], row[3], row[4], json.loads(row[5])))
        return map_designs

    def insert_feature(self, feature: Feature):
        query = '''
        INSERT INTO "feature" (territory_name, simple_feature_data, simple_feature_type, note, url, last_update)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        self.conn.execute(query, (feature.territory_name, feature.simple_feature_data, feature.simple_feature_type,
                                  feature.note, feature.url, feature.last_update.isoformat()))
        self.conn.commit()

    def get_feature(self, feature_id: int) -> Feature:
        query = 'SELECT * FROM "feature" WHERE id = ?'
        cursor = self.conn.execute(query, (feature_id,))
        row = cursor.fetchone()
        if row:
            return Feature(row[1], row[2], row[3], row[4], row[5], datetime.fromisoformat(row[6]))
        return None

    def update_feature(self, feature_id: int, feature: Feature):
        query = '''
        UPDATE "feature"
        SET territory_name = ?, simple_feature_data = ?, simple_feature_type = ?, note = ?, url = ?, last_update = ?
        WHERE id = ?
        '''
        self.conn.execute(query, (feature.territory_name, feature.simple_feature_data, feature.simple_feature_type,
                                  feature.note, feature.url, feature.last_update.isoformat(), feature_id))
        self.conn.commit()

    def delete_feature(self, feature_id: int):
        query = 'DELETE FROM "feature" WHERE id = ?'
        self.conn.execute(query, (feature_id,))
        self.conn.commit()

    def list_features(self) -> List[Feature]:
        query = 'SELECT * FROM "feature"'
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
