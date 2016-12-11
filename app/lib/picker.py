import operator
import ssh
import db


def getDiff(change_set):
    client = ssh.Paramiko('hwe-launcher42-vm.eng.vmware.com', 'root', 'ca$hc0w')
    if change_set:
        client.send('p5 diff --show-c-function -c %s' % change_set)
        return client.receive() 
    return ''

def getChangedFunc(change_set):
    diff = getDiff(change_set)
    #print diff
    f_list = []
    for line in diff.split('\n'):
        if "***************" in line and "(" in line:
            line = line.split('(')[0]
            line = line.split()[-1]
            f_list.append(line)
    #print f_list
    return set(f_list)

def getTestCase(con, change_set, driver):
    f_list = getChangedFunc(change_set)
    con.getDB('KMBCOV')
    con.getCollection(driver)
    record_list = con.coll.find({'driver': driver})
    case_dict = {}
    no_function_list = []
    for record in record_list:
        tmp_fun_cov = record['cov_data']['funcCovs']
        testid = record['testid']
        weight = 0
        for f_name in f_list:
            try:
                if not tmp_fun_cov[f_name]['hits']:
                    continue
                else:
                    weight += 1
            except KeyError:
                if f_name not in no_function_list:
                    no_function_list.append(f_name)
        if not weight:
            continue
        case_weight = {testid:weight}
        case_dict.update(case_weight)
    #print case_dict
    sorted_case_list = sorted(case_dict.items(), key=operator.itemgetter(1),reverse=True)
    return sorted_case_list


if __name__ == '__main__':
    con = db.mongo('10.117.5.169', 27017)
    con.getConnection()
    print getTestCase(con, '4394402', 'ne1000')
