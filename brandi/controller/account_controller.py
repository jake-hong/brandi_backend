from service.account_service import AccountService
from model.account_dao import AccountDao
from utils import login_decorator, error_code, master_only, check_param
from connection import get_connection
from config import SECRET, ALGORITHM
from flask_request_validator import validate_params, Param, GET, PATH, JSON, Pattern, MaxLength, FORM
from flask import Blueprint, request, jsonify
import schema
import requests
import jwt
import bcrypt
import pymysql
import os
import sys
import re
re


account_app = Blueprint('account_app', __name__)
account_dao = AccountDao()


class Account:
    """Account 뷰 
    Authors: 홍성은
    History: 2020-10-24 초기생성
             2020-10-26 수정 
    """
    @account_app.route('/signup', methods=['POST'])
    # 파라미터 유효성 검사
    @validate_params(
        Param('identification', JSON, str, rules=[Pattern(
            r'^[a-zA-Z][0-9a-zA-Z_-]{4,15}$')]),  # 영문으로 시작, 숫자,영문대소문자 포함, 5글자 이상 15글자 미만
        Param('password', JSON, str, rules=[MaxLength(20)]),  # 비밀번호 최대 20자
        Param('account_type_id', JSON, str, int),
        Param('contact', JSON, str, rules=[
              Pattern(r'\d{3}-\d{4}-\d{4}')]),  # 전화번호 형식
        Param('attribute_id', JSON, str, int),
        Param('korean_name', JSON, str, rules=[
              Pattern(r'[ㄱ-힣a-zA-Z0-9]')]),  # 한글, 영문, 숫자만 입력
        Param('english_name', JSON, str, rules=[
              Pattern(r'[a-z]')]),  # 셀러 영문명은 소문자만 가능
        Param('cs_contact', JSON, str, rules=[
              Pattern(r'\d{2,3}-\d{3,4}-\d{4}')]),  # 숫자와 하이픈만 입력
    )
    def signup_post(*args):
        """회원가입 API입니다.
        Args: body로 오는 값
            identification  : 셀러 아이디,
            password        : 비밀번호,
            account_type_id : 계정유형 PK(마스터,셀러),
            contact         : 핸드폰번호,
            attribute_id    : 셀러유형 PK(쇼핑몰,마켓),
            korean_name     : 셀러명(상호),
            english_name    : 영문 셀러명(영문상호),
            cs_contact      : 고객센터 전화번호
        Returns: 
            회원가입 성공, 200 : {'message': 'SUCCESS'} 
            아이디 중복,  409  : {'error': 'A1021}
            DB 연결 실패 : {'error':'C0002'}
        Authors: 홍성은
        History: 
            2020-10-25    : 초기 생성
            2020-10-26~28 : 유효성검사 추가, 로직 변경 
            2020-10-28    : validation 추가 
        """
        try:
            get_connection()
            db_connection = get_connection()
            # validation 확인 완료 후 request로 받은 데이터 변수화
            seller_info = {
                'identification': args[0],
                'password': args[1],
                'account_type_id': args[2],
                'contact': args[3],
                'attribute_id': args[4],
                'korean_name': args[5],
                'english_name': args[6],
                'cs_contact': args[7],
            }

            # DB 연결 후 account_service의 seller_info 로직 진행된 결과값 return
            if db_connection:
                account_service = AccountService()
                result = account_service.signup(
                    seller_info, db_connection=db_connection)
                # DB 입력
                db_connection.commit()
                return result
            return jsonify({'message': 'INVALID_CONNECTION'}), 500

        except Exception as exception:
            return error_code({'error': 'C0002', 'programming_error': exception})

        finally:
            try:
                # DB 종료
                db_connection.close()
            except Exception as exception:
                return error_code({'error': 'C0003', 'programming_error': exception})

    @account_app.route('/seller', methods=['GET'])
    # @login_decorator
    # 파라미터 유효성 검사
    @validate_params(
        Param('id', GET, str, required=False, default=None),
        Param('identification', GET, str, required=False, default=None),
        Param('english_name', GET, str, required=False, default=None),
        Param('korean_name', GET, str, required=False, default=None),
        Param('manager_name', GET, str, required=False, default=None),
        Param('status_name', GET, str, required=False, default=None),
        Param('contact', GET, str, required=False, default=None),
        Param('email', GET, str, required=False, default=None),
        Param('attribute', GET, str, required=False, default=None),
        Param('start_date', GET, str, required=False),
        Param('end_date', GET, str, required=False),
        Param('offset', GET, int, required=False),
        Param('limit', GET, int, required=False)
    )
    def get_seller_list(*args):
        """모든 셀러회원의 리스트를 보여주는 API 입니다. 
        Args:
            offset: 각 페이지 시작 번호   
            limit : 페이지 당 제한 수
        Returns: 셀러 리스트
            'seller_list':[{
                    'id'             : 셀러id
                    'created_at'     : 생성일, 
                    'identification' : 아이디,
                    'english_name'   : 영문 셀러명, 
                    'korean_name'    : 셀러명,
                    'name'           : 담당자 이름,
                    's.name'         : 셀러 상태,
                    'contact'        : 담당자 연락처,
                    'email'          : 이메일,
                    'at.name'        : 셀러 속성
                }],200 
            'C0002' : {'message': 'DB_ERROR', 'client_message': 'DB_Connection 실패', 'code': 501}
            'A1061' : {'message': 'INVALID_PAGE','client_message':'페이지가 유효하지 않습니다.','code':400}, 
            'A1043' : {'message': 'UNAUTHORIZED', 'client_message': '접근 불가능한 페이지입니다.', 'code': 403},  
        Authors: 홍성은 

        History: 2020-10-27 : 초기 생성
                 2020-11-01 : 필터 생성 
                 2020-11-03 : 페이지네이션 생성 
        """
        db_connection = get_connection()

        # validation 통과한 값 seller_list로 변수화
        seller_list = {
            'id': args[0],
            'identification': args[1],
            'english_name': args[2],
            'korean_name': args[3],
            'manager_name': args[4],
            'status_name': args[5],
            'contact': args[6],
            'email': args[7],
            'attribute': args[8],
            'start_date': args[9],
            'end_date': args[10],
            'offset': args[11] if args[11] else 0,
            'limit': args[12] if args[12] else 10,
        }
        # 등록기간 시작날짜, 종료날짜 정의
        start_date = args[9]
        end_date = args[10]

        # 두 값 모두 들어올 경우 에러 발생하기 때문에 종료날짜가 시작날짜보다 늦으면 시작기간과 종료날짜 동일
        if start_date and end_date:
            if start_date > end_date:
                start_date = end_date
        # DB 연결
        try:
            if db_connection:
                account_service = AccountService()
                result = account_service.get_seller_list(
                    seller_list, db_connection=db_connection)
                return jsonify(result)

        except Exception as error:
            return error_code({'error': 'A1043'})

        finally:
            try:
                db_connection.close()
            except Exception as exception:
                return error_code({'error': 'C0003', 'programming_error': exception})

    @account_app.route("/signin", methods=['POST'])
    def sign_in():
        """
        로그인 API [POST]
        작성자: 김수정
        Args:
            account_id  : 유저 id
            password    : 비밀번호
        Returns:
            Success     : {Authorization : {'account_id': token}
                            is_master   : True / False,
                            filter_list : {},
                            nav_list    : {}
                        }, 200
            key error   : {message : KEY_ERROR}, 400
            로그인 ID 오류   : {message : USER_DOES_NOT_EXIST}, 400
            비밀번호 불일치   : {message' : INVALID ACCESS} 400
        """
        # parameter 확인
        body = request.json
        try:
            body = request.json
            essens_params = [
                (str, body['identification']),
                (str, body['password'])
            ]

            check_check = check_param(essens_params)
            if check_check:
                print(check_check)
                return error_code(check_check)

        except TypeError as exception:
            return error_code({'error': 'C0006', 'programming_error': exception})

        except Exception as exception:
            return error_code({'error': 'C0001', 'programming_error': exception})

        # DB 연결
        try:
            db_connection = get_connection()

            account_service = AccountService()
            result = account_service.signin(body, db_connection)

            # 로그인 성공한 경우
            if 'success' in result:
                return jsonify(result), 200

            # 로그인 실패
            else:
                return error_code(result)

        # DB 연결 실패
        except Exception as exception:
            # db_connection.rollback()
            return error_code({"error": "C0002", 'programming_error': exception})

        # DB Close
        finally:
            try:
                if db_connection:
                    db_connection.close()
            except Exception as exception:
                return error_code({"error": "C0003", 'programming_error': exception})

    @account_app.route("/sellerDetail/<int:seller_id>", methods=['GET'])
    @login_decorator
    def get_seller_info(seller_id):
        """
        셀러 정보 수정 페이지에서 기존 데이터를 호출 API [GET]
        작성자: 김수정
        Args:
            seller_id  : 상세 정보 보고자 하는 셀러의 account_id
        Returns:
            Success     : {Authorization : {'account_id': token} }, 200
            key error   : {message : KEY_ERROR}, 400
        """
        # parameter 확인
        try:
            essens_params = [
                (int, seller_id)
            ]

            check_check = check_param(essens_params)

            if check_check:
                return error_code(check_check)

        except TypeError as exception:
            return error_code({'error': 'C0006', 'programming_error': exception})

        except Exception as exception:
            return error_code({'error': 'C0001', 'programming_error': exception})

        # DB 연결
        try:
            db_connection = get_connection()

            account_service = AccountService()
            result = account_service.get_seller_info(
                seller_id, db_connection, request)

            # 성공
            if 'success' in result:
                return jsonify(result), 200

            # 실패
            else:
                return error_code(result)

            return error_code({'error': 'A1031'})

        # DB 연결 실패
        except Exception as exception:
            return error_code({"error": "C0002", 'programming_error': exception})

        # DB Close
        finally:
            try:
                if db_connection:
                    db_connection.close()
            except Exception as exception:
                return error_code({"error": "C0003", 'programming_error': exception})

    @account_app.route("/action", methods=['POST'])
    @master_only
    def change_seller_status():
        """
        셀러의 입점상태를 변경해주는 함수 [POST]
        작성자: 김수정
        Args:
            seller_id   : 타깃 유저의 account id 
            action_id   : 취할 액션의 id (
        Returns:
            Success     : 

        """
        # parameter 확인
        try:
            body = request.json
            essens_params = [
                (int, body['seller_id']),
                (int, body['action_id'])
            ]

            check_check = check_param(essens_params)

            if check_check:
                return error_code(check_check)

        except TypeError as exception:
            return error_code({'error': 'C0006', 'programming_error': exception})

        except Exception as exception:
            return error_code({'error': 'C0001', 'programming_error': exception})

        # DB 연결
        try:
            db_connection = get_connection()

            account_service = AccountService()
            print(request.account_id)
            result = account_service.change_seller_status(db_connection, body)

            # 성공
            if 'success' in result:
                db_connection.commit()
                return jsonify(result), 200

            # 실패
            else:
                db_connection.rollback()
                return error_code(result)

        # DB 연결 실패
        except Exception as exception:
            return error_code({"error": "C0002", 'programming_error': exception})

        # DB Close
        finally:
            try:
                if db_connection:
                    db_connection.close()
            except Exception as exception:
                return error_code({"error": "C0003", 'programming_error': exception})
