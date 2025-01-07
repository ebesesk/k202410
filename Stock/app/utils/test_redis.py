import redis
import json
import os, sys
import time  # time.sleep을 사용하기 위해 추가
from datetime import datetime, timedelta


REDIS_CLIENT = redis.Redis(
        host='localhost',
        port=6379,
        db = 0,
        decode_responses=True
    )

def read_json_lines(file_path):
    data_list = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():  # 빈 줄 제외
                    try:
                        data = json.loads(line)
                        data_list.append(data)
                        # # NWS가 아닌 데이터만 추가
                        # if data['header']['tr_cd'] != 'NWS':
                        #     data_list.append(data)
                    except json.JSONDecodeError as e:
                        print(f"JSON 파싱 오류: {e}")
                        continue
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
    
    return data_list

def redis_publish(channel, data):
    REDIS_CLIENT.publish(channel, json.dumps(data, ensure_ascii=False))
    # print(json.dumps(data, ensure_ascii=False))


def test_redis_juga_publish():
    file_path = '/home/kds/k202410/Stock/app/utils/websocket_response.json'
    data = read_json_lines(file_path)

    index = 0
    data_length = len(data)
    print('data_length:', data_length)
    # 1분 후의 종료 시간 설정
    end_time = datetime.now() + timedelta(minutes=0.5)

    while datetime.now() < end_time and index < 20:  # 현재 시간이 종료 시간보다 작을 때만 실행
        if index >= data_length:  # 데이터 끝에 도달하면 처음으로 돌아감
            index = 0
            
        
        channel = 'stock'
        # print(index, '_____', data[index]['body']['price'], data[index]['body']['chetime'])
        # redis_publish(channel, json.dumps(data[index], ensure_ascii=False))
        redis_publish(channel, data[index])
        # print('redis_publish: ', channel, json.dumps(data[index], ensure_ascii=False))
        index += 1
        time.sleep(0.5)

    print("1분이 경과하여 프로그램을 종료합니다.")