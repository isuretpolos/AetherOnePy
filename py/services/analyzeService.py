import sys, os, random

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.databaseService import get_case_dao
from services.hotbitsService import HotbitsService, HotbitsSource
from domains.aetherOneDomains import AnalysisRate


def transformAnalyzeListToDict(rates: []):
    dictList = []
    for rate in rates:
        dictList.append(rate.to_dict())
    return dictList


def analyze(analysis_id: int, rates: list, hotbits_service: HotbitsService, autoCheckGV:bool = False, enhancedAnalysis:bool = False) -> list:

    if rates is None or len(rates) == 0:
        return []

    enhanced_rates = []

    # PRE-SELECTION
    # FIRST ITERATION
    if not enhancedAnalysis:
        # DEFAULT PRE-SELECTION
        countSelected = 0
        random.shuffle(rates)
        while countSelected < 24 and len(rates) > 0:
            countSelected += 1
            rate = rates.pop(hotbits_service.getInt(0, len(rates)))  # random select 24 rates
            newRate = AnalysisRate(rate.signature, rate.description, rate.catalogID, analysis_id, 0, 0,
                                   0, "", 0, "")
            newRate.id = rate.id
            enhanced_rates.append(newRate)
    else:
        # ADVANCED PRE-SELECTION
        for rate in rates:
            newRate = AnalysisRate(rate.signature, rate.description, rate.catalogID, analysis_id, 0, 0,
                                   0, "", 0, "")
            newRate.id = rate.id
            enhanced_rates.append(newRate)
        # assign +1 to value until 20 of them reach at least a value 10
        while True:
            for rate in enhanced_rates:
                random_value = hotbits_service.getInt(1, 5)
                if random_value == 5:
                    rate.energetic_value += 1
            if len(enhanced_rates) < 20:
                break
            countSelected = 0
            for rate in enhanced_rates:
                if rate.energetic_value > 10:
                    countSelected += 1
            if countSelected >= 20:
                break
        # CLEAN ALL NON WORTHY
        enhanced_rates = [rate for rate in enhanced_rates if rate.energetic_value >= 11]

    # SECOND ITERATION, assign 0 to 10 until at least one reach 1000
    # from this point there is no difference between advanced or default analysis
    maxReached = False

    while maxReached == False:
        for rate in enhanced_rates:
            rate.energetic_value += hotbits_service.getInt(0, 10)

            if rate.energetic_value >= 1000:
                maxReached = True
                break

    enhanced_rates.sort(key=lambda r: r.energetic_value, reverse=True)

    if len(enhanced_rates) > 24:
        enhanced_rates = enhanced_rates[0:24]

    if autoCheckGV:
        for rate in enhanced_rates:
            rate.gv = checkGeneralVitality(hotbits_service)

    return enhanced_rates


def checkGeneralVitality(hotbits_service: HotbitsService):
    list = []
    for i in range(3):
        list.append(hotbits_service.getInt(0,1000))

    list.sort(reverse=True)
    gv = list[0]

    if gv > 950:
        randomDice = hotbits_service.getInt(0,100)

        while randomDice >= 50:
            gv += randomDice
            randomDice = hotbits_service.getInt(0, 100)
    return gv


# Example Usage
if __name__ == "__main__":
    aetherOneDB = get_case_dao(os.path.join(PROJECT_ROOT, 'data/aetherone.db'))
    catalogs = aetherOneDB.list_catalogs()
    rates_list = aetherOneDB.list_rates_from_catalog(catalogs[0].id)
    hotbits = HotbitsService(HotbitsSource.WEBCAM, os.path.join(PROJECT_ROOT, "hotbits"))
    #rates_list = [
    #    Rate("R1", "Rate 1 Description", 101),
    #    Rate("R2", "Rate 2 Description", 102),
    #    Rate("R3", "Rate 3 Description", 103)
    #]

    enhanced_rates = analyze(rates_list, hotbits)

    for rate in enhanced_rates:
        rate.gv = checkGeneralVitality(hotbits)
        print(f"Signature: {rate.signature}, Value: {rate.value}, GV: {rate.gv}")
