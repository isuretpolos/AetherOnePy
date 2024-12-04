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


class Session:
    def __init__(self, intention: str, description: str, created: datetime, caseID: int):
        self.id = 0
        self.intention = intention
        self.description = description
        self.created = created
        self.caseID = caseID


class Analysis:
    def __init__(self, note: str, created: datetime = datetime.now()):
        self.id = 0
        self.note = note
        self.sessionID = 0
        self.created = created


# A catalog describes a set of rates, for example homeopathy, or rates from specific authors
class Catalog:
    def __init__(self, name: str, description: str, author: str, importdate: datetime):
        self.id = 0
        self.name = name
        self.description = description
        self.author = author
        self.importdate = importdate


# A rate is a carrier for intention, a link towards a morphic field
class Rate:
    def __init__(self, signature: str, description: str, catalogID: int):
        self.id = 0
        self.signature = signature
        self.description = description  # Markdown
        self.catalogID = catalogID


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
    def __init__(self, occurrence: int, overall_energetic_value: int, overall_gv: int, name: str, originalRateId: int,
                 analysisId: int):
        self.occurrence = occurrence
        self.overall_energetic_value = overall_energetic_value
        self.overall_gv = overall_gv
        self.name = name
        self.originalRateId = originalRateId
        self.analysisId = analysisId


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