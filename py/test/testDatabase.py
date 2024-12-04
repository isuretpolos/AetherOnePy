# TEST Database Design and Functionality and a "breakthrough" combining all elements
import os, sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domains.aetherOneDomains import Case, Session, Analysis
from services.databaseService import get_case_dao

if __name__ == '__main__':
    # init DAO
    dao = get_case_dao("testdb")
    # insert 2 cases
    dao.insert_case(Case('testCase1', 'test1@test.de', '#fff', 'a test case 1', datetime.now(), datetime.now()))
    dao.insert_case(Case('testCase2', 'test2@test.de', '#fff', 'a test case 2', datetime.now(), datetime.now()))
    # read all cases
    listCases = dao.list_cases()

    for caseObj in listCases:
        # show some of the data
        print(
            f"CASE ID {caseObj.id} | NAME {caseObj.name} | COLOR {caseObj.color} | DESCRIPTION '{caseObj.description}'")

        # add a session to each case
        dao.insert_session(Session('balance energy', 'description', datetime.now(), caseObj.id), caseObj.id)

        # list sessions of the case
        listSessions = dao.list_sessions(caseObj.id)

        for sessionObj in listSessions:
            print(f"  SESSION ID {sessionObj.id} | INTENTION {sessionObj.intention} | DESCRIPTION '{sessionObj.description}'")
            # Add an analysis
            dao.insert_analysis(Analysis('test analysis'), sessionObj.id)

    dao.close()
    os.remove("testdb")