def make_payload_1(csrf, sem_sub_id, authorized_id, timestamp):
    return {
        "_csrf": csrf,
        "paramReturnId": "getCourseForCoursePage",
        "semSubId": sem_sub_id,
        "authorizedID": authorized_id,
        "x": timestamp
    }

def make_payload_2(csrf, class_id,sem_sub_id, authorized_id,timestamp):
    return {
        "_csrf": csrf,
        "classId": class_id,
        "praType": "source",
        "paramReturnId": "getSlotIdForCoursePage",
        "semSubId": sem_sub_id,
        "authorizedID": authorized_id,
        "x": timestamp
    }

def make_payload_3(csrf,sem_sub_id, authorized_id,timestamp):
    return {
        "_csrf": csrf,
        "semesterSubId": sem_sub_id,
        "authorizedID": authorized_id,
        "x": timestamp
    }

def make_payload_4(csrf,sem_sub_id,erp_id,class_id,authorized_id,timestamp):
    return {
        "_csrf": csrf,
        "semSubId": sem_sub_id,
        "erpId": erp_id,
        "classId": class_id,
        "authorizedID": authorized_id,
        "x": timestamp
    }

def make_payload_5(csrf,authorized_id,timestamp):
    return {
        "authorizedID": authorized_id,
        "_csrf": csrf,
        "x": timestamp
    }