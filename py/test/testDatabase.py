# TEST Database Design and Functionality and a "breakthrough" combining all elements
import os, sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domains.aetherOneDomains import Case, Session, Analysis
from services.databaseService import get_case_dao

if __name__ == '__main__':
    # init DAO
    dao = get_case_dao("test.db")
    try:
        # insert 2 cases
        dao.insert_case(Case('testCase1', 'test1@test.de', '#fff', 'a test case 1', datetime.now(), datetime.now()))
        dao.insert_case(Case('testCase2', 'test2@test.de', '#fff', 'a test case 2', datetime.now(), datetime.now()))
        # read all cases
        listCases = dao.list_cases()
        assert len(listCases) == 2

        for caseObj in listCases:
            # show some of the data
            print(f"CASE ID {caseObj.id} | NAME {caseObj.name} | COLOR {caseObj.color} | DESCRIPTION '{caseObj.description}' | CREATED {caseObj.created}")

            # add a session to each case
            dao.insert_session(Session('balance energy', 'description', caseObj.id), caseObj.id)

            # list sessions of the case
            listSessions = dao.list_sessions(caseObj.id)
            assert len(listSessions) == 1

            for sessionObj in listSessions:
                print(f"  SESSION ID {sessionObj.id} | INTENTION {sessionObj.intention} | DESCRIPTION '{sessionObj.description}'")
                # Add an analysis
                dao.insert_analysis(Analysis('test analysis'), sessionObj.id)
                listAnalysis = dao.list_analysis(sessionObj.id)
                assert len(listAnalysis) == 1

                for analysis in listAnalysis:
                    print(f"  ANALYSIS ID {analysis.id} | NOTE {analysis.note} | CREATED '{analysis.created}'")

                sessionObj = dao.get_session(sessionObj.id)
                assert sessionObj is not None

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
        print(len(listCases))
        assert len(listCases) == 0

    finally:
        dao.close()
        os.remove("test.db")
