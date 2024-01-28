import json
import requests
import datetime

requests.packages.urllib3.disable_warnings()


APP_KEY = "36c6b40c411d476080a58ad2fcc01c49"
APP_SECRET = "dbabeb22491cffeb1695b94830a4a369"
HEADERS = {'Host': 'open.ys7.com', 'Content-Type': 'application/x-www-form-urlencoded'}
session = requests.Session()
session.headers.update(HEADERS)

def get_access_token():
    token_url = f'https://open.ys7.com/api/lapp/token/get?appKey={APP_KEY}&appSecret={APP_SECRET}'
    response = session.post(token_url, verify=False)
    assert response.status_code == 200, f"请求失败, {response.content.decode()}"
    access_token = response.json()["data"]["accessToken"]
    return access_token


def get_camera_list(access_token, page_start: int = 0, page_size: int = 100) -> list:
    body = {"pageSize": page_size, "pageNo": page_start}
    url = f"https://open.ys7.com/api/lapp/device/list?accessToken={access_token}&pageStart={page_start}&pageSize={page_size}"
    response = session.post(url, data=json.dumps(body), verify=False)
    assert response.status_code == 200, f"请求失败, {response.content.decode()}"
    data = response.json().get("data")
    # data 示例如下:
    # [{'id': 'ee0f9382b18941788afb21f5cccb2836E11709236', 'deviceSerial': 'E11709236', 'deviceName': 'DS-8864N-K8(E11709236)', 'deviceType': 'DS-8864N-K8', 'status': 1, 'defence': 0, 'deviceVersion': 'V3.4.107 build 190927', 'addTime': 1597918478868, 'updateTime': 1597918478000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194'}, {'id': 'ee0f9382b18941788afb21f5cccb2836F18524544', 'deviceSerial': 'F18524544', 'deviceName': 'DS-7832N-R2(F18524544)车间', 'deviceType': 'DS-7832N-R2', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.30.011 build 200803', 'addTime': 1617341316967, 'updateTime': 1617341316000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194'}, {'id': 'ee0f9382b18941788afb21f5cccb2836F18524587', 'deviceSerial': 'F18524587', 'deviceName': 'DS-7832N-R2(F18524587)车间2', 'deviceType': 'DS-7832N-R2', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.30.011 build 200803', 'addTime': 1617341319747, 'updateTime': 1617341319000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194'}, {'id': 'ee0f9382b18941788afb21f5cccb2836G48942863', 'deviceSerial': 'G48942863', 'deviceName': 'DS-8864N-R8(G48942863)', 'deviceType': 'DS-8864N-R8', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.30.071 build 210616', 'addTime': 1631077394683, 'updateTime': 1675991157000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194'}, {'id': 'ee0f9382b18941788afb21f5cccb2836J51116746', 'deviceSerial': 'J51116746', 'deviceName': '农博园种植基地', 'deviceType': 'CS-C5W-3H2FL4GA-B', 'status': 0, 'defence': 0, 'deviceVersion': 'V5.3.0 build 230301', 'addTime': 1665816823609, 'updateTime': 1698367008000, 'parentCategory': 'IPC', 'riskLevel': 0, 'netAddress': '117.61.242.132'}, {'id': 'ee0f9382b18941788afb21f5cccb2836J63493307', 'deviceSerial': 'J63493307', 'deviceName': '农博园种植基地2', 'deviceType': 'CS-C5W-3H2FL4GA-B', 'status': 0, 'defence': 0, 'deviceVersion': 'V5.3.0 build 230301', 'addTime': 1665816365225, 'updateTime': 1703814867000, 'parentCategory': 'IPC', 'riskLevel': 0, 'netAddress': '202.62.115.99'}, {'id': 'ee0f9382b18941788afb21f5cccb2836J84284955', 'deviceSerial': 'J84284955', 'deviceName': 'HNVR5104(J84284955)', 'deviceType': 'HNVR5104', 'status': 0, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1657678565432, 'updateTime': 1698731272000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '117.176.147.245'}, {'id': 'ee0f9382b18941788afb21f5cccb2836J94946511', 'deviceSerial': 'J94946511', 'deviceName': 'HNVR5108(J94946511)', 'deviceType': 'HNVR5108', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1657602251210, 'updateTime': 1706044117000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194'}, {'id': 'ee0f9382b18941788afb21f5cccb2836K07164123', 'deviceSerial': 'K07164123', 'deviceName': 'HNVR5216(K07164123)', 'deviceType': 'HNVR5216', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1662028645354, 'updateTime': 1706306239000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '117.139.222.31'}, {'id': 'ee0f9382b18941788afb21f5cccb2836K07164167', 'deviceSerial': 'K07164167', 'deviceName': 'HNVR5216(K07164167)', 'deviceType': 'HNVR5216', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1680248563846, 'updateTime': 1706306264000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '117.139.222.31'}, {'id': 'ee0f9382b18941788afb21f5cccb2836K20324550', 'deviceSerial': 'K20324550', 'deviceName': 'HNVR5104(K20324550)', 'deviceType': 'HNVR5104', 'status': 0, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1659431769955, 'updateTime': 1698761054000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '117.176.147.245'}, {'id': 'ee0f9382b18941788afb21f5cccb2836K20324575', 'deviceSerial': 'K20324575', 'deviceName': 'HNVR5104(K20324575)', 'deviceType': 'HNVR5104', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1659245215459, 'updateTime': 1706044117000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194'}, {'id': 'ee0f9382b18941788afb21f5cccb2836K20324631', 'deviceSerial': 'K20324631', 'deviceName': 'HNVR5104(K20324631)', 'deviceType': 'HNVR5104', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1659242992164, 'updateTime': 1706044116000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194'}, {'id': 'ee0f9382b18941788afb21f5cccb2836K20324634', 'deviceSerial': 'K20324634', 'deviceName': 'HNVR5104(K20324634)', 'deviceType': 'HNVR5104', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1659244194397, 'updateTime': 1706044115000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194'}, {'id': 'ee0f9382b18941788afb21f5cccb2836K20324637', 'deviceSerial': 'K20324637', 'deviceName': 'HNVR5104(K20324637)', 'deviceType': 'HNVR5104', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1659240386338, 'updateTime': 1706058079000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194'}]
    return data


def get_camera_m3u8url(access_token, device_serial, protocol: int =2):
    url = f"https://open.ys7.com/api/lapp/v2/live/address/get?accessToken={access_token}&deviceSerial={device_serial}&protocol={protocol}&supportH265=0"
    response = session.post(url, verify=False)
    assert response.status_code == 200, f"请求失败, {response.content.decode()}"
    # print(response.content.decode())
    data = response.json().get("data")  # 如果摄像头报错会获取不到data
    # data 示例如下:
    # {"id":"671317735942139904","url":"https://open.ys7.com/v3/openlive/K07164123_1_1.m3u8?expire=1706413020&id=671317735942139904&t=571b8861cd961b6a1627cc31e4672c1f31ada3cbc7f68703a2597198eb0a1d0b&ev=100","expireTime":"2024-01-28 11:37:00"}
    return data


def get_all_camera_m3u8url():
    token = get_access_token()
    camera_list = get_camera_list(token)
    for camera in camera_list:
        if camera["status"] == 1:            # status 为0即设备已下线, 为1即在线.
            data = get_camera_m3u8url(token, camera["deviceSerial"])
            url = data["url"]
            expire_time = data["expireTime"]    # expire_time 应该是摄像头m3u8url的过期时间
            camera.update({"expire_time": expire_time, "url": url})
    return camera_list


# print(get_all_camera_m3u8url())
# [{'id': 'ee0f9382b18941788afb21f5cccb2836E11709236', 'deviceSerial': 'E11709236', 'deviceName': 'DS-8864N-K8(E11709236)', 'deviceType': 'DS-8864N-K8', 'status': 1, 'defence': 0, 'deviceVersion': 'V3.4.107 build 190927', 'addTime': 1597918478868, 'updateTime': 1597918478000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194', 'expire_time': '2024-01-28 22:13:00', 'url': 'https://open.ys7.com/v3/openlive/E11709236_1_1.m3u8?expire=1706451180&id=671477789699969024&t=47d21b39445147ee41d34a630499e1600c405f8d1f4d89510210f203c9523068&ev=100'}, {'id': 'ee0f9382b18941788afb21f5cccb2836F18524544', 'deviceSerial': 'F18524544', 'deviceName': 'DS-7832N-R2(F18524544)车间', 'deviceType': 'DS-7832N-R2', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.30.011 build 200803', 'addTime': 1617341316967, 'updateTime': 1617341316000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194', 'expire_time': '2024-01-28 22:13:00', 'url': 'https://open.ys7.com/v3/openlive/F18524544_1_1.m3u8?expire=1706451180&id=671477790104621056&t=f59d2b18fd2ac50150becace7f2036bc64406cdce57cb3c574ba907d404cd022&ev=100'}, {'id': 'ee0f9382b18941788afb21f5cccb2836F18524587', 'deviceSerial': 'F18524587', 'deviceName': 'DS-7832N-R2(F18524587)车间2', 'deviceType': 'DS-7832N-R2', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.30.011 build 200803', 'addTime': 1617341319747, 'updateTime': 1617341319000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194', 'expire_time': '2024-01-28 22:13:00', 'url': 'https://open.ys7.com/v3/openlive/F18524587_1_1.m3u8?expire=1706451180&id=671477790423388160&t=e9bf92677c2bd99b0b7225c369c55cb84c39353e91ea484444cb7fedc92519c4&ev=100'}, {'id': 'ee0f9382b18941788afb21f5cccb2836G48942863', 'deviceSerial': 'G48942863', 'deviceName': 'DS-8864N-R8(G48942863)', 'deviceType': 'DS-8864N-R8', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.30.071 build 210616', 'addTime': 1631077394683, 'updateTime': 1675991157000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194', 'expire_time': '2024-01-28 22:13:00', 'url': 'https://open.ys7.com/v3/openlive/G48942863_1_1.m3u8?expire=1706451180&id=671477790639493120&t=bcec158fbc2b6f320d786a4c820cfc780c55254196d2bcaa6fd281ca66786ab2&ev=100'}, {'id': 'ee0f9382b18941788afb21f5cccb2836J51116746', 'deviceSerial': 'J51116746', 'deviceName': '农博园种植基地', 'deviceType': 'CS-C5W-3H2FL4GA-B', 'status': 0, 'defence': 0, 'deviceVersion': 'V5.3.0 build 230301', 'addTime': 1665816823609, 'updateTime': 1698367008000, 'parentCategory': 'IPC', 'riskLevel': 0, 'netAddress': '117.61.242.132'}, {'id': 'ee0f9382b18941788afb21f5cccb2836J63493307', 'deviceSerial': 'J63493307', 'deviceName': '农博园种植基地2', 'deviceType': 'CS-C5W-3H2FL4GA-B', 'status': 0, 'defence': 0, 'deviceVersion': 'V5.3.0 build 230301', 'addTime': 1665816365225, 'updateTime': 1703814867000, 'parentCategory': 'IPC', 'riskLevel': 0, 'netAddress': '202.62.115.99'}, {'id': 'ee0f9382b18941788afb21f5cccb2836J84284955', 'deviceSerial': 'J84284955', 'deviceName': 'HNVR5104(J84284955)', 'deviceType': 'HNVR5104', 'status': 0, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1657678565432, 'updateTime': 1698731272000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '117.176.147.245'}, {'id': 'ee0f9382b18941788afb21f5cccb2836J94946511', 'deviceSerial': 'J94946511', 'deviceName': 'HNVR5108(J94946511)', 'deviceType': 'HNVR5108', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1657602251210, 'updateTime': 1706044117000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194', 'expire_time': '2024-01-28 22:13:00', 'url': 'https://open.ys7.com/v3/openlive/J94946511_1_1.m3u8?expire=1706451180&id=671477790972850176&t=3374514988891fb024dac43e952a908b80bbdb415c9beeae166e42c54ab68569&ev=100'}, {'id': 'ee0f9382b18941788afb21f5cccb2836K07164123', 'deviceSerial': 'K07164123', 'deviceName': 'HNVR5216(K07164123)', 'deviceType': 'HNVR5216', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1662028645354, 'updateTime': 1706306239000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '117.139.222.31', 'expire_time': '2024-01-28 22:13:00', 'url': 'https://open.ys7.com/v3/openlive/K07164123_1_1.m3u8?expire=1706451180&id=671477791481843712&t=c94f614b593fabb2a6f2da2fc90f40a11504d666ea274aae129ff60dc20eefe7&ev=100'}, {'id': 'ee0f9382b18941788afb21f5cccb2836K07164167', 'deviceSerial': 'K07164167', 'deviceName': 'HNVR5216(K07164167)', 'deviceType': 'HNVR5216', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1680248563846, 'updateTime': 1706306264000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '117.139.222.31', 'expire_time': '2024-01-28 22:13:01', 'url': 'https://open.ys7.com/v3/openlive/K07164167_1_1.m3u8?expire=1706451181&id=671477791828484096&t=616bab1eb0a00896dd0d088ec1bed46afa1e4f707f503f2ea0a34e0f51a6e5b7&ev=100'}, {'id': 'ee0f9382b18941788afb21f5cccb2836K20324550', 'deviceSerial': 'K20324550', 'deviceName': 'HNVR5104(K20324550)', 'deviceType': 'HNVR5104', 'status': 0, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1659431769955, 'updateTime': 1698761054000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '117.176.147.245'}, {'id': 'ee0f9382b18941788afb21f5cccb2836K20324575', 'deviceSerial': 'K20324575', 'deviceName': 'HNVR5104(K20324575)', 'deviceType': 'HNVR5104', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1659245215459, 'updateTime': 1706044117000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194', 'expire_time': '2024-01-28 22:13:01', 'url': 'https://open.ys7.com/v3/openlive/K20324575_1_1.m3u8?expire=1706451181&id=671477792175853568&t=3c3455052d2d4139d2eee2d9802b65ba085ef68c3f0f91e40794558498fbb038&ev=100'}, {'id': 'ee0f9382b18941788afb21f5cccb2836K20324631', 'deviceSerial': 'K20324631', 'deviceName': 'HNVR5104(K20324631)', 'deviceType': 'HNVR5104', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1659242992164, 'updateTime': 1706044116000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194', 'expire_time': '2024-01-28 22:13:01', 'url': 'https://open.ys7.com/v3/openlive/K20324631_1_1.m3u8?expire=1706451181&id=671477792688316416&t=4cc56c6b788cc5bcd4b4810ab1f1226ddde5a82d554628d299149ef733cf8b30&ev=100'}, {'id': 'ee0f9382b18941788afb21f5cccb2836K20324634', 'deviceSerial': 'K20324634', 'deviceName': 'HNVR5104(K20324634)', 'deviceType': 'HNVR5104', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1659244194397, 'updateTime': 1706044115000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194', 'expire_time': '2024-01-28 22:13:01', 'url': 'https://open.ys7.com/v3/openlive/K20324634_1_1.m3u8?expire=1706451181&id=671477792958943232&t=d6d25d4454578661ebc0aa413e7cfb91b42397448d4efe09c7862ad6d6d9f886&ev=100'}, {'id': 'ee0f9382b18941788afb21f5cccb2836K20324637', 'deviceSerial': 'K20324637', 'deviceName': 'HNVR5104(K20324637)', 'deviceType': 'HNVR5104', 'status': 1, 'defence': 0, 'deviceVersion': 'V4.31.130 build 220325', 'addTime': 1659240386338, 'updateTime': 1706058079000, 'parentCategory': 'COMMON', 'riskLevel': 0, 'netAddress': '223.87.40.194', 'expire_time': '2024-01-28 22:13:01', 'url': 'https://open.ys7.com/v3/openlive/K20324637_1_1.m3u8?expire=1706451181&id=671477793509642240&t=665ee31892d5073a6a4e604777a711c81f791d8e9f817c8110cfb6fdf58c0d34&ev=100'}]


def is_expired(expire_time):
    expire_date = datetime.datetime.strptime(expire_time, "%Y-%m-%d %H:%M:%S")
    now_expire = datetime.datetime.now()
    if now_expire > expire_date:
        return True
    else:
        return False


def is_expired_date(expire_time: datetime.datetime):
    now = datetime.datetime.now()
    if now > expire_time:
        return True
    else:
        return False

def date_string_to_datetime(expire_time: str):
    return datetime.datetime.strptime(expire_time, "%Y-%m-%d %H:%M:%S")


