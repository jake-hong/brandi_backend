from slacker import Slacker
import os
import jwt
from flask import jsonify, Response, request
from config import SECRET,ALGORITHM, BRANDI_TOKEN, CHANNEL_ID
from functools  import wraps 
from connection import get_connection
from model.account_dao import AccountDao

account_dao = AccountDao()

def login_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization', None)

        if not token: 
            return error_code({'error':'A1041'})

        try:
            db_connection = get_connection()
        except Exception as exception:
            return error_code({'error':'A1043'})

        try:
            decoded_token = jwt.decode(token, SECRET, ALGORITHM)
            account_id = decoded_token['account_id']
            is_master = account_dao.check_master(db_connection, {'account_id':account_id})
            
            if is_master:
                request.account_id  = decoded_token['account_id']
                request.is_master = True
            else:
                request.account_id = decoded_token['account_id']
                request.is_master = False
                    
        except jwt.exceptions.DecodeError as exception:
            return error_code({'error':'A1042', 'programming_error':exception})
        finally:
            try:
                if db_connection:
                    db_connection.close()
            except Exception as exception:
                return error_code({"error":"C0003", 'programming_error':exception})

        return func(*args, **kwargs) 
    return wrapper

def master_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        token = request.headers.get('Authorization', None)

        if not token: 
            return error_code({'error':'A1041'})

        try:
            db_connection = get_connection()
        except Exception as exception:
            return error_code({'error':'A1043'})

        try:
            decoded_token = jwt.decode(token, SECRET, ALGORITHM)
            account_id = decoded_token['account_id']
            is_master = account_dao.check_master(db_connection, {'account_id':account_id})

            if is_master:
                request.account_id  = decoded_token['account_id']
                request.is_master = True
            else:
                return error_code({'error':'A1043'})

        except jwt.exceptions.DecodeError as exception:
            return error_code({'error':'A1042', 'programming_error':exception})
        return func(*args, **kwargs) 
    return wrapper

def error_code(error_dict):
    """ 에러코드 및 에러메세지 관리
    args: 
        {'error' : "에러 코드 번호", 'programming_error: exception} 
    Returns: 
        Error message & code dictionary
    Authors: 김수정 / 홍성은
    History:
        2020-10-27 : 초기 생성
    """
    codes = {
    # A (Account)
        # 로그인 A1010
        'A1011' : {'message': 'INVALID USER', 'client_message': '아이디를 확인하세요', 'code': 401}, 
        'A1012' : {'message': 'WRONG PASSWORD', 'client_message': '비밀번호를 확인하세요', 'code': 401}, 
        'A1013' : {'message': 'KEY_ERROR', 'client_message': '필수정보를 입력하세요', 'code': 401}, 
        'A1014' : {'message': 'NOT VALIDATED YET', 'client_message': '입점 승인 후 이용 가능합니다', 'code': 401}, 

        # 회원가입 1020
        'A1021' : {'message': 'DUPLICATED_ID', 'client_message': '중복되는 아이디 입니다.', 'code': 409},
        'A1022' : {'message': 'INVALID_SELLER_INFO', 'client_message': '셀러 정보 없음', 'code': 400},
        'A1023' : {'message': 'INVALID_MANAGER_INFO', 'client_message': '매니저 정보 없음', 'code': 400}, 
        'A1024' : {'message': 'DUPLICATED_KOREAN_NAME', 'client_message': '셀러명 중복', 'code': 400},
        'A1025' : {'message': 'DUPLICATED_ENGLISH_NAME', 'client_message': '영문 셀러명 중복', 'code': 400},
        

        # 셀러정보보기 1030
        'A1031' : {'message': 'NO_ACCOUNT', 'client_message': '요청한 셀러 정보 없음', 'code': 400},

        # 로그인 데코레이터 A1041
        'A1041' : {'message': 'NO TOKEN', 'client_message': '로그인 이후 사용 가능합니다.', 'code': 408}, 
        'A1042' : {'message': 'INVALID TOKEN', 'client_message': '로그인 이후 사용 가능합니다.', 'code': 409}, 
        'A1043' : {'message': 'UNAUTHORIZED', 'client_message': '접근 불가능한 페이지입니다.', 'code': 403}, 
        
        # 셀러 상태 변경 A1050
        'A1051' : {'message': 'INVALID_REQUEST', 'client_message': '셀러 상태를 재확인하세요.', 'code': 400}, 

        # 셀러 리스트 A1060
        'A1061' : {'message': 'INVALID_PAGE','client_message':'페이지가 유효하지 않습니다.','code':400}, 
        'A1062' : {'message': 'INVALID_PAGE','client_message':'인자가 유효하지 않습니다.','code':400},
    
    # P (Product)
        # 주문하기 2010
        'P2011' : {'message': 'INVALID_PRODUCT', 'client_message': '조회 불가능한 상품입니다', 'code': 400}, 
        'P2012' : {'message': 'INVALID_PRODUCT', 'client_message': '판매가 종료된 상품입니다', 'code': 400}, 
        'P2013' : {'message': 'INVALID_PRODUCT', 'client_message': '현재 미판매중인 상품입니다', 'code': 400}, 
        'P2014' : {'message': 'INVALID_OPTION_QUANTITY', 'client_message': '옵션과 수량을 다시 선택해 주세요', 'code': 400}, 
        'P2015' : {'message': 'INVALID_QUANTITY', 'client_message': '수량을 조정해주세요', 'code': 400}, 

        # 상품 상태 변경 2020
        'P2021' : {'message': 'NO DETAIL REQUEST', 'client_message': '변경 내용을 전송하세요', 'code': 400}, 
    
    # O (Order)
        # 주문 상태 변경 3010
        'O3011' : {'message': 'REQUEST DOES NOT MATCH', 'client_message': '주문의 상태를 다시 확인하세요', 'code': 400}, 


    # C (공통)
        'C0001' : {'message': 'KEY_ERROR', 'client_message': '필수정보를 입력하세요', 'code': 401}, 
        'C0002' : {'message': 'DB_ERROR', 'client_message': 'DB_Connection 실패', 'code': 501}, 
        'C0003' : {'message': 'DB_ERROR', 'client_message': 'DB_Closing 실패', 'code': 501}, 
        'C0004' : {'message': 'NO_AUTHORIZATION', 'client_message': '마스터 이외 접근 불가', 'code': 400}, 
        'C0005' : {'message': 'KEY_TYPE ERROR', 'client_message': '데이터 타입 확인하세요', 'code': 400}, 
        'C0006' : {'message': 'NO DATA', 'client_message': '데이터를 전송하세요', 'code': 400}, 
        'C0007' : {'message': 'NO_AUTHORIZATION', 'client_message': '셀러 이외 접근 불가', 'code': 400}, 

    }

    if 'programming_error' in error_dict:
        codes[error_dict['error']]['programming_error'] = error_dict['programming_error'].args
    
    return jsonify( codes[error_dict['error']]   ), codes[error_dict['error']]['code']
    
def check_param(essens_params):
    for key, value in essens_params:
        if key != type(value):
            return {'error':'C0005'}

def get_filter(db_connection, is_master):
    """
    로그인시 마스터/셀러 구분에 따라 필요한 필터를 return 합니다. 
    args: 
        is_master : T/F
    Returns: 
        필터
    Authors: 김수정
    History:
        2020.11.01 : 초기 생성
    """

    filter_list = [
        {
        'id': 'sale',
        'filterTitle': '판매여부',
        'category': [
            {
            'category_id': '',
            'category_title': '전체',
            },
            {
            'category_id': 1,
            'category_title': '판매',
            },
            {
            'category_id': 0,
            'category_title': '미판매',
            },
        ],
        },
        {
        'id': 'display',
        'filterTitle': '진열여부',
        'category': [
            {
            'category_id': '',
            'category_title': '전체',
            },
            {
            'category_id': 1,
            'category_title': '진열',
            },
            {
            'category_id': 0,
            'category_title': '미진열',
            },
        ],
        },
        {
        'id': 'discount',
        'filterTitle': '할인여부',
        'category': [
            {
            'category_id': '',
            'category_title': '전체',
            },
            {
            'category_id': 1,
            'category_title': '할인',
            },
            {
            'category_id': 0,
            'category_title': '미할인',
            },
        ],
        },
    ]

    if is_master:
        filter_list.append(
                {
                    'id': 'seller_name',
                    'filterTitle': '셀러명',
                }
            )

        attribute_total = {'category_id':'', 'category_title':'전체'}
        attribute_result = account_dao.get_attributes(db_connection)['attributes']

        attributes = attribute_result.insert(0, attribute_total)

        filter_list.append(
                {
                    'id': 'attribute',
                    'filterTitle': '셀러속성',
                    'category': attribute_result
                }
        )

    return filter_list

def nav_to_dict(nav_rows):
    """
    dao 에서 불러온 네비게이션 바를 가공합니다. 
    작성자: 김수정
    Args:
        db_connection : db
        nav_rows      : 네비게이션 바 정보
    Returns:
    """
    api_naming = {
        '홈':'home', 
        '통계':'', 
        '주문관리':'order', 
        '취소/환불관리':'', 
        '상품관리':'product', 
        '고객응대관리':'', 
        '기획전/쿠폰관리':'', 
        '회원 관리':'account',
        '공지사항':'',
        '정산관리':'',
        '진열관리':''
    }
    
    sub_api_naming = {
        '홈':'',
        '생략':'', 
        '전체주문관리':'allOrderList', #성은
        '상품준비관리':'prepareList', #성은
        '배송준비관리':'deliveryPrepareList', #성은 
        '배송중관리':'deliveryList', #성은
        '배송완료관리':'deliveryCompleteList', #성은
        '구매확정관리':'orderConfirmList', #성은
        '상품관리':'', #수정
        '상품등록':'', #성은
        '회원 관리_커뮤니티':'', 
        '셀러 계정 관리':'seller', # 성은
        '셀러 정보 관리':'sellerDetail', #수정
        '회원 관리':'',
        '페널티 셀러 관리':'',
        '도매처 관리':''
    }

    nav_list = []
    nav_index = []
    for row in nav_rows:

        if row['menu_id'] not in nav_index:
            temp_dict = {}
            temp_dict['id'] = row['menu_id']
            temp_dict['menu_title'] = row['menu']
            temp_dict['main_url'] = api_naming[row['menu']]
            temp_dict['sub_menus'] = [
                {
                'sub_menu_id' : row['sub_menu_id'], 
                'sub_menu_title': row['sub_menu'], 
                'sub_url':sub_api_naming[row['sub_menu']]
                }
            ]
            
            nav_index.append(row['menu_id'])
            nav_list.append(temp_dict)
        
        else:
            index = nav_index.index(row['menu_id']) 
            nav_list[index]['sub_menus'].append(
                {
                'sub_menu_id' : row['sub_menu_id'], 
                'sub_menu_title':row['sub_menu'], 
                'sub_url':sub_api_naming[row['sub_menu']]
                }
            )

    return nav_list

def send_slack(buyer_name, product_name, status_name):
    """
    주문의 배송상태가 변경될 때마다 slack 메세지를 전송합니다.  
    Args:
        buyer_name   : 주문자 명
        product_name : 상품명
        status_name  : 현재 상품의 배송상태
    Author : 김수정
    History: 
        2020-11-01: 초기생성
    """
    slack = Slacker(BRANDI_TOKEN)

    msg = f"""{buyer_name} 님이 주문하신 상품 안내 드립니다.
    상품명 : {product_name}
    상태  :  {status_name}
            -브랜디 """

    slack.chat.post_message(CHANNEL_ID, msg)