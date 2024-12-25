# TEST Database Design and Functionality and a "breakthrough" combining all elements
import os, sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domains.aetherOneDomains import Case, Session, Analysis, Catalog, Rate, AnalysisRate
from services.databaseService import get_case_dao

if __name__ == '__main__':
    # init DAO
    dao = get_case_dao("test.db")
    try:

        listCatalogs = dao.list_catalogs()
        assert len(listCatalogs) == 0
        dao.insert_catalog(Catalog('Morphic Fields','List of special energies', 'Isuret Polos'))
        dao.insert_catalog(Catalog('A Dictionary of Practical Materia Medica','List of homeopathic remedies', 'John Henry Clarke'))
        listCatalogs = dao.list_catalogs()
        assert len(listCatalogs) == 2
        assert listCatalogs[0].id == 1
        assert listCatalogs[1].id == 2
        catalogMorphic = dao.get_catalog(1)
        assert catalogMorphic is not None
        print(catalogMorphic.to_dict())

        catalogMorphic = dao.get_catalog_by_name('Morphic Fields')
        assert catalogMorphic is not None

        dao.delete_catalog(catalogMorphic.id)
        catalogMorphic = dao.get_catalog(1)
        assert catalogMorphic is None
        catalogClarke = dao.get_catalog(2)
        assert catalogClarke is not None
        print(catalogClarke.to_dict())
        dao.insert_rate(Rate('Arnica','bruises, doesn''t want to be touched', catalogClarke.id))
        dao.insert_rate(Rate('Sulfur','lazy and always theorizing', catalogClarke.id))
        dao.insert_rate(Rate('Zincum','repetitive tasks, works too much', catalogClarke.id))
        rateArnica = dao.get_rate(1)
        assert rateArnica is not None
        print(rateArnica.to_dict())
        rates = dao.list_rates_from_catalog(catalogClarke.id)
        assert len(rates) == 3

        for rate in rates:
            print(rate.to_dict())
            dao.delete_rate(rate.id)

        rates = dao.list_rates_from_catalog(catalogClarke.id)
        assert len(rates) == 0

        listCases = dao.list_cases()
        assert len(listCases) == 0
        # insert 2 cases
        dao.insert_case(Case('testCase1', 'test1@test.de', '#fff', 'a test case 1', datetime.now(), datetime.now()))
        dao.insert_case(Case('testCase2', 'test2@test.de', '#fff', 'a test case 2', datetime.now(), datetime.now()))
        # read all cases
        listCases = dao.list_cases()
        assert len(listCases) == 2

        for caseObj in listCases:
            # show some of the data
            print(
                f"CASE ID {caseObj.id} | NAME {caseObj.name} | COLOR {caseObj.color} | DESCRIPTION '{caseObj.description}' | CREATED {caseObj.created}")

            # add a session to each case
            dao.insert_session(Session('balance energy 1', 'description', caseObj.id))
            dao.insert_session(Session('balance energy 2', 'description', caseObj.id))

            # list sessions of the case
            listSessions = dao.list_sessions(caseObj.id)
            assert len(listSessions) == 2
            assert caseObj.id > 0

            last_session = dao.get_last_session(caseObj.id)
            assert last_session is not None
            print(f"  LAST SESSION ID {last_session.id} | INTENTION {last_session.intention} | DESCRIPTION '{last_session.description} | CREATED {last_session.created}'")

            for sessionObj in listSessions:
                print(f"  SESSION ID {sessionObj.id} | INTENTION {sessionObj.intention} | DESCRIPTION '{sessionObj.description} | CREATED {sessionObj.created}'")
                # Add some analysis
                dao.insert_analysis(Analysis('test analysis 1', sessionObj.id))
                dao.insert_analysis(Analysis('test analysis 2', sessionObj.id))
                listAnalysis = dao.list_analysis(sessionObj.id)
                assert len(listAnalysis) == 2
                assert sessionObj.id > 0

                last_analysis = dao.get_last_analysis(sessionObj.id)
                assert last_analysis is not None
                print(f"    LAST ANALYSIS ID {last_analysis.id} | NOTE {last_analysis.note} | CREATED '{last_analysis.created}'")

                for analysis in listAnalysis:
                    print(f"    ANALYSIS ID {analysis.id} | NOTE {analysis.note} | CREATED '{analysis.created}'")
                    analysis.note = f"{analysis.note} UPDATED"
                    dao.update_analysis(analysis)
                    analysis = dao.get_analysis(analysis.id)
                    assert analysis is not None
                    assert analysis.note.endswith("UPDATED")
                    assert analysis.sessionID == sessionObj.id
                    assert analysis.id > 0

                    # Create a list of AnalysisRate objects
                    analysis_rates = [
                        AnalysisRate("Sig1", "Description1", 1, analysis.id, 100, 50, 3, "Type1", 10, "Note1"),
                        AnalysisRate("Sig2", "Description2", 2, analysis.id, 200, 60, 4, "Type2", 20, "Note2"),
                    ]

                    dao.insert_rates_for_analysis(analysis_rates)
                    analysis_rates = dao.list_rates_for_analysis(analysis.id)

                    assert analysis_rates is not None
                    assert len(analysis_rates) == 2

                    for rate in analysis_rates:
                        print(f"      ANALYSIS_RATE ID {rate.id} | SIGNATURE {rate.signature}")

                    dao.delete_analysis(analysis.id)
                    analysis = dao.get_analysis(analysis.id)
                    assert analysis is None

                listAnalysis = dao.list_analysis(sessionObj.id)
                assert len(listAnalysis) == 0

                sessionObj = dao.get_session(sessionObj.id)
                assert sessionObj is not None
                assert sessionObj.id > 0
                dao.delete_session(sessionObj.id)
                sessionObj = dao.get_session(sessionObj.id)
                assert sessionObj is None

            listSessions = dao.list_sessions(caseObj.id)
            assert len(listSessions) == 0

            caseObj.name = f"{caseObj.name} UPDATED"
            dao.update_case(caseObj)

            caseObj = dao.get_case(caseObj.id)
            assert caseObj is not None
            assert caseObj.name.endswith("UPDATED")
            print(f"CASE ID {caseObj.id} | NAME {caseObj.name} | COLOR {caseObj.color} | DESCRIPTION '{caseObj.description}' | CREATED {caseObj.created}")
            dao.delete_case(caseObj.id)

            caseObj = dao.get_case(caseObj.id)
            assert caseObj is None

        listCases = dao.list_cases()
        assert len(listCases) == 0

    finally:
        dao.close()
        os.remove("test.db")
