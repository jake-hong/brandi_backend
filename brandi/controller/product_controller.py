import pymysql 
import requests

from flask import Blueprint,request,jsonify

from connection import get_connection
from utils import login_decorator, error_code, master_only, check_param

from model.product_dao import ProductDao
from service.product_service import ProductService 

product_app = Blueprint('product_app',__name__)

product_service = ProductService()

class Product:
    @product_app.route("", methods=['GET'])
    @login_decorator
    def get_product_list(*args):
        """
        등록된 상품들의 목록을 불러오는 API
        작성자: 김수정
        Args:
            filter_dict : query 
        Returns:
        """
        # DB 연결
        try:
            db_connection = get_connection()

            filter_dict = request.args
            result = product_service.get_product_list(db_connection, filter_dict)

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

    @product_app.route('', methods=['POST'])
    @login_decorator
    def change_product_status():
        """
        선택한 상품의 판매/진열 여부를 수정하는 API
        작성자: 김수정
        Args:
            displayed : 0 or 1 
            sales     : 0 or 1 
            product_ids : [상품 번호들]
        Returns:
        """

        body = request.json
        try:
            body = request.json
            essens_params = [
                (int, body.get('displayed', 1)),
                (int, body.get('sales', 1)),
                (list, body['product_ids'])   
            ]

            # 판매/미판매 & 진열/미진열 바꿔줄 내용이 안 온 경우
            if (not body.get('displayed', None) in (0,1))\
                and (not body.get('sales', None) in (0,1)):
                return error_code({'error':"P2021"})

            check_check = check_param(essens_params)

            if check_check:
                return error_code(check_check)

        except TypeError as exception:
            return error_code({'error':'C0006', 'programming_error':exception})
        
        except Exception as exception:
            return error_code({'error':'C0001', 'programming_error':exception})

        # DB 연결
        try:
            db_connection = get_connection()
            result = product_service.change_status(db_connection, body)

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
                    db_connection.commit()
                    db_connection.close()
            except Exception as exception:
                return error_code({"error":"C0003", 'programming_error':exception})