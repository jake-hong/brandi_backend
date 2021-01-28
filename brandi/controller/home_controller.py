import os, sys, re 

import pymysql 
import requests
from flask import Blueprint,request,jsonify

from connection import get_connection
from utils import login_decorator, error_code, master_only, check_param
from model.account_dao import AccountDao
from service.account_service import AccountService 

home_app = Blueprint('home_app',__name__)
account_dao = AccountDao()

class Home:
    @home_app.route("", methods=['GET'])
    @login_decorator
    def home(): 
        """
        셀러 로그인 후 보이는 Home 페이지
        작성자: 김수정
        Args:
            account_id  : 유저 id
        Returns:
            Success     : {매출 통계} 
        """
        #DB 연결
        try:
            db_connection = get_connection()

            account_service = AccountService()
            is_master = request.is_master
            
            if is_master: #마스터인 경우 접근 불가
                return error_code({'error':'C0007'})

            # 셀러인 경우
            else:
                result = account_service.get_home_info(db_connection)
            
                # 성공
                if 'success' in result:
                    return jsonify(result), 200

                # 실패 
                else:
                    return error_code(result)

        # DB 연결 실패 
        except Exception as exception:
            return error_code({"error":"C0002", 'programming_error':exception})

        # DB Close
        finally:
            try:
                if db_connection:
                    db_connection.close()
            except Exception as exception:
                return error_code({"error":"C0003", 'programming_error':exception})