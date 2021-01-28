import pymysql
# import boto3

from config import DATABASES

""" 데이터베이스 커넥션 생성
Args: import 될 때 마다 데이터베이스 커넥션 생성

Returns: database connection 객체

Authors: 홍성은

History:
    2020-10-26 : 초기 생성
"""


def get_connection():
    return pymysql.connect(
        user=DATABASES['user'],
        password=DATABASES['password'],
        host=DATABASES['host'],
        port=DATABASES['port'],
        database=DATABASES['database'],
        cursorclass=pymysql.cursors.DictCursor,
    )
