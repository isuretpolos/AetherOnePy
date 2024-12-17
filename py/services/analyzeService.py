import sys, os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.databaseService import get_case_dao
from services.hotbitsService import HotbitsService, HotbitsSource


class Rate:
    def __init__(self, signature: str, description: str, catalogID: int):
        self.id = 0
        self.signature = signature
        self.description = description  # Markdown
        self.catalogID = catalogID
        self.value = 0  # This will store the enhanced value
        self.gv = 0


def analyze(rates: list, hotbits_service: HotbitsService, autoCheckGV:bool = False) -> list:

    newRates = []
    for rate in rates:
        newRate = Rate(rate.signature,rate.description,rate.catalogID)
        newRate.id = rate.id
        newRates.append(newRate)

    enhanced_rates = newRates

    # PRE-SELECTION
    # FIRST ITERATION, assign +1 to value until 20 of them reach at least a value 10
    while True:
        for rate in enhanced_rates:
            random_value = hotbits_service.getInt(1, 5)
            if random_value == 5:
                rate.value += 1

        if len(enhanced_rates) < 20:
            break

        countSelected = 0
        for rate in enhanced_rates:
            if rate.value > 10:
                countSelected += 1

        if countSelected >= 20:
            break

    # CLEAN ALL NOT WORTHY
    enhanced_rates = [rate for rate in enhanced_rates if rate.value >= 11]

    # SECOND ITERATION, assign 0 to 10 until at least one reach 1000
    maxReached = False

    while maxReached == False:
        for rate in enhanced_rates:
            rate.value += hotbits_service.getInt(0, 10)

            if rate.value >= 1000:
                maxReached = True
                break

    enhanced_rates.sort(key=lambda r: r.value, reverse=True)

    if autoCheckGV:
        for rate in enhanced_rates:
            rate.gv = checkGeneralVitality(hotbits)

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
    aetherOneDB = get_case_dao('../../data/aetherone.db')
    catalogs = aetherOneDB.list_catalogs()
    rates_list = aetherOneDB.list_rates_from_catalog(catalogs[0].id)
    hotbits = HotbitsService(HotbitsSource.WEBCAM, "../../hotbits")
    #rates_list = [
    #    Rate("R1", "Rate 1 Description", 101),
    #    Rate("R2", "Rate 2 Description", 102),
    #    Rate("R3", "Rate 3 Description", 103)
    #]

    enhanced_rates = analyze(rates_list, hotbits)

    for rate in enhanced_rates:
        rate.gv = checkGeneralVitality(hotbits)
        print(f"Signature: {rate.signature}, Value: {rate.value}, GV: {rate.gv}")
