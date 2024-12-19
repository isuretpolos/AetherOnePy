from datetime import datetime


# Scenarios:
# A case describes a target, with different situations (sessions), an initial analysis, the continuing balancing and
# a final conclusion.  Inbetween are the rates, the collections of rates and correlations between them.
# Energy is between the words and around them.
# Special objects are maps, timelines, space-time visualization, cards, images, sounds and so on.
# During a session occur multiple analysis and broadcasts.
# Each analysis has a set of rates (AnalysisRate) persisted in the database.
# Checking the GV after one broadcast is virtually a new analysis, so it will generate a new set of rates (copies).
class Case:
    def __init__(self, name: str, email: str, color: str, description: str, created: datetime,
                 last_change: datetime):
        self.id = 0
        self.name = name
        self.email = email
        self.color = color
        self.description = description
        self.created = created
        self.last_change = last_change

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'color': self.color,
            'description': self.description,
            'created': self.created.isoformat(),
            'last_change': self.last_change.isoformat()
        }


class Session:
    def __init__(self, intention: str, description: str, caseID: int):
        self.id = 0
        self.intention = intention
        self.description = description
        self.created = datetime.now()
        self.caseID = caseID

    def to_dict(self):
        return {
            'id': self.id,
            'intention': self.intention,
            'description': self.description,
            'created': self.created.isoformat(),
            'caseID': self.caseID
        }


class Analysis:
    def __init__(self, note: str, created: datetime = datetime.now()):
        self.id = 0
        self.note = note
        self.sessionID = 0
        self.created = created

    def to_dict(self):
        return {
            'id': self.id,
            'note': self.note,
            'sessionID': self.sessionID,
            'created': self.created.isoformat()
        }


# A catalog describes a set of rates, for example homeopathy, or rates from specific authors
class Catalog:
    def __init__(self, name: str, description: str, author: str, importdate: datetime = datetime.now()):
        self.id = 0
        self.name = name
        self.description = description
        self.author = author
        self.importdate = importdate

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'author': self.author,
            'importdate': self.importdate.isoformat()
        }


# A rate is a carrier for intention, a link towards a morphic field
class Rate:
    def __init__(self, signature: str, description: str, catalogID: int):
        self.id = 0
        self.signature = signature
        self.description = description  # Markdown
        self.catalogID = catalogID

    def to_dict(self):
        return {
            'id': self.id,
            'signature': self.signature,
            'description': self.description,
            'catalogID': self.catalogID
        }


class BroadCastData:
    def __init__(self, clear: bool, intention: str, signature: str, delay: int, repeat: int,
                 entering_with_general_vitality: int, leaving_with_general_vitality: int, sessionID: int,
                 created: datetime):
        self.id = 0
        self.clear = clear
        self.intention = intention
        self.signature = signature
        self.delay = delay
        self.repeat = repeat
        self.entering_with_general_vitality = entering_with_general_vitality
        self.leaving_with_general_vitality = leaving_with_general_vitality
        self.sessionID = sessionID
        self.created = created


class AnalysisRate:
    def __init__(self, signature: str, description: str, catalog_id: int, analysis_id: int, energetic_value: int,
                 gv: int, level: int, potency_type: str, potency: int, note: str):
        self.id = 0
        self.signature = signature
        self.description = description
        self.catalog_id = catalog_id
        self.analysis_id = analysis_id
        self.energetic_value = energetic_value
        self.gv = gv
        self.level = level
        self.potency_type = potency_type
        self.potency = potency
        self.note = note

    def to_dict(self):
        return {
            "id": self.id,
            "signature": self.signature,
            "description": self.description,
            "catalog_id": self.catalog_id,
            "analysis_id": self.analysis_id,
            "energetic_value": self.energetic_value,
            "gv": self.gv,
            "level": self.level,
            "potency_type": self.potency_type,
            "potency": self.potency,
            "note": self.note,
        }

    def to_tuple(self):
        return (
            self.signature,
            self.description,
            self.catalog_id,
            self.analysis_id,
            self.energetic_value,
            self.gv,
            self.level,
            self.potency_type,
            self.potency,
            self.note
        )


class MapDesign:
    def __init__(self, uuid: str, coordinates_x: int, coordinates_y: int, zoom: int):
        self.id = 0
        self.uuid = uuid
        self.coordinates_x = coordinates_x
        self.coordinates_y = coordinates_y
        self.zoom = zoom


class Feature:
    def __init__(self, territory_name: str, simple_feature_data: str, simple_feature_type: str, note: str, url: str,
                 last_update: datetime):
        self.id = 0
        self.territory_name = territory_name
        self.simple_feature_data = simple_feature_data
        self.simple_feature_type = simple_feature_type
        self.note = note
        self.url = url
        self.last_update = last_update
