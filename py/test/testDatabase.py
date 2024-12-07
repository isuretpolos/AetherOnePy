# TEST Database Design and Functionality and a "breakthrough" combining all elements
import os, sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domains.aetherOneDomains import Case, Session, Analysis, Catalog
from services.databaseService import get_case_dao

if __name__ == '__main__':
    # init DAO
    dao = get_case_dao("test.db")
    try:

        listCatalogs = dao.list_catalogs()
        assert len(listCatalogs) == 0
        dao.insert_catalog(Catalog('Morphic Fields','List of special energies', 'Isuret Polos'))
        dao.insert_catalog(Catalog('A Dictionary of Practical Materia Medica','List of special energies', 'John Henry Clarke'))
        listCatalogs = dao.list_catalogs()
        assert len(listCatalogs) == 2
        assert listCatalogs[0].id == 1
        assert listCatalogs[1].id == 2
        catalogMorphic = dao.get_catalog(1)
        assert catalogMorphic is not None
        print(catalogMorphic.to_dict())
        dao.delete_catalog(catalogMorphic.id)
        catalogMorphic = dao.get_catalog(1)
        assert catalogMorphic is None

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
            dao.insert_session(Session('balance energy 1', 'description', caseObj.id), caseObj.id)
            dao.insert_session(Session('balance energy 2', 'description', caseObj.id), caseObj.id)

            # list sessions of the case
            listSessions = dao.list_sessions(caseObj.id)
            assert len(listSessions) == 2
            assert caseObj.id > 0

            for sessionObj in listSessions:
                print(f"  SESSION ID {sessionObj.id} | INTENTION {sessionObj.intention} | DESCRIPTION '{sessionObj.description} | CREATED {sessionObj.created}'")
                # Add some analysis
                dao.insert_analysis(Analysis('test analysis 1'), sessionObj.id)
                dao.insert_analysis(Analysis('test analysis 2'), sessionObj.id)
                listAnalysis = dao.list_analysis(sessionObj.id)
                assert len(listAnalysis) == 2
                assert sessionObj.id > 0

                for analysis in listAnalysis:
                    print(f"  ANALYSIS ID {analysis.id} | NOTE {analysis.note} | CREATED '{analysis.created}'")
                    analysis.note = f"{analysis.note} UPDATED"
                    dao.update_analysis(analysis)
                    analysis = dao.get_analysis(analysis.id)
                    assert analysis is not None
                    assert analysis.note.endswith("UPDATED")
                    assert analysis.sessionID == sessionObj.id
                    assert analysis.id > 0
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
