import os
import sys
import re
import pymysql
import requests

from flask import Blueprint, request, jsonify

from connection import get_connection
from utils import login_decorator, error_code, master_only, check_param, send_slack
from flask_request_validator import GET, PATH, Param, JSON, validate_params

from model.product_dao import ProductDao
from model.account_dao import AccountDao
from model.order_dao import OrderDao

from service.order_service import OrderService
from service.product_service import ProductService

order_app = Blueprint('order_app', __name__)
order_service = OrderService()
product_service = ProductService()


class Order:
    @order_app.route("/<int:product_id>", methods=['GET'])
    # @login_decorator
    def get_options(product_id):
        """
        상품을 구매하기 위해 해당 상품의 옵션 정보를 불러오는 API 입니다.
        작성자: 김수정
        Args:
            product_id : 구매할 상품 번호(path parameter) 
        Returns:
        """
        # parameter 확인
        try:
            essens_params = [
                (int, product_id)
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
            result = product_service.get_options_service(
                db_connection, product_id)

            # 성공
            if 'success' in result:
                return jsonify(result), 200

            # 실패
            else:
                return error_code(result)

        # DB 연결 실패
        except Exception as exception:
            return error_code({"error": "C0003", 'programming_error': exception})

        # DB Close
        finally:
            try:
                if db_connection:
                    db_connection.close()
            except Exception as exception:
                return error_code({"error": "C0007", 'programming_error': exception})

    @order_app.route("/<int:product_id>", methods=['POST'])
    # @login_decorator
    def make_order(product_id):
        """
        옵션 선택 후 배송지 정보를 입력하여 상품을 주문하는 API
        작성자: 김수정
        Args:
            product_id : 구매할 상품 번호 (path parameter)
            color_id   : 선택한 색상 번호
            size_id    : 선택한 사이즈 번호
            quantity   : 수량
            buyer_name : 수령인 이름
            contact    : 수령인 전화번호
            zip_code   : 수령지 우편번호
            street_address : 수령지 주소
            detail_address : 수령지 상세주소
        Returns:
        """
        # parameter 확인
        try:
            body = request.json
            essens_params = [
                (int, product_id),
                (int, body['color_id']),
                (int, body['size_id']),
                (int, body['size_id']),
                (int, body['quantity']),
                (str, body['buyer_name']),
                (str, body['contact']),
                (str, body['zip_code']),
                (str, body['street_address']),
                (str, body['detail_address'])
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

            result = order_service.make_order_service(
                db_connection, product_id, body)

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
            db_connection.rollback()
            return error_code({"error": "C0002", 'programming_error': exception})

        # DB Close
        finally:
            try:
                if db_connection:
                    db_connection.close()
            except Exception as exception:
                return error_code({"error": "C0003", 'programming_error': exception})

    @order_app.route("/change", methods=['POST'])
    @login_decorator
    def change_order_status():
        """
        선택한 주문의 배송 상태를 변경합니다. 
        작성자: 김수정
        Args:
            body   : 딕셔너리
                {detail_order_ids : 배송상태 변경할 주문들의 번호(list)}
                {status_before:
                status_after}
        Returns:
        """
        # parameter 확인
        try:
            body = request.json
            essens_params = [
                (list, body['id']),
                (int, body['status_id']),
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
            result = order_service.make_order_progress(
                db_connection, request.account_id, body)

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
            db_connection.rollback()
            return error_code({"error": "C0002", 'programming_error': exception})

        # DB Close
        finally:
            try:
                if db_connection:
                    db_connection.close()
            except Exception as exception:
                return error_code({"error": "C0003", 'programming_error': exception})

    @order_app.route("/<order_status_name>", methods=['GET'])
    @validate_params(
        Param('order_status_name', PATH, str, required=True),
        Param('start_date', GET, int, required=False),
        Param('end_date', GET, int, required=False),
        Param('order_number', GET, int, required=False),
        Param('detail_order_id', GET, str, required=False),
        Param('product_name', GET, str, required=False),
        Param('reciever_name', GET, int, required=False),
        Param('phone_number', GET, int, required=False),
        Param('offset', GET, int, required=False),
        Param('limit', GET, int, required=False),
    )
    # @login_decorator
    def get_order_list(*args):
        print(args)
        """결제완료된 리스트를 표출합니다.
        Args: 
            order_info: 결제 리스트
            db_connection: 연결된 db
            offset: 각 페이지 시작 번호 
            limit : 페이지에 들어갈 리스트 수
        Returns: 결제 완료 리스트 
            'order_info' : [{
                 paied_at             : 결제일자
                 order_id               : 주문번호
                 name                 : 상품명
                 detail_orders.id       : 주문상세번호
                 korean_name          : 셀러명
                 detail_orders.quantity : 수량
                 option_id              : 옵션정보
                 contact              : 핸드폰번호 
                 name                 : 주문자명
                 total_paied_price    : 결제 금액 
                 name                 : 주문 상태 
            }]     
        Authors: 
            홍성은 
        History:
            2020-11-03: 초기 생성 
        """
        # PATH 파라미터로 order_status_name 사용 order_status_dict에 있는 키값 넣을 경우 해당 페이지로 넘어감.
        order_status_dict = {
            'allOrderList': None,
            'prepareList': 2,
            'deliveryPrepareList': 3,
            'deliveryList': 4,
            'deliveryCompleteList': 5,
            'orderConfirmList': 6,
        }
        print(order_status_dict)
        db_connection = get_connection()
        # validation 확인 완료 후 request로 받은 데이터 변수화

        order_info = {
            'status_id': order_status_dict[args[0]],
            'start_date': args[1],  # 검색시작일
            'end_date': args[2],  # 검색완료일
            'order_number': args[3],  # 주문번호
            'detail_order_id': args[4],  # 주문상세번호
            'product_name': args[5],  # 상품명
            'receiver_name': args[6],  # 주문자명
            'phone_number': args[7],  # 핸드폰번호
            'offset': args[8] if args[8] else 0,
            'limit': args[9] if args[9] else 10
        }
        print(order_info)
        try:
            # DB 연결 확인
            if db_connection:
                result = order_service.get_complete_order(
                    order_info, db_connection=db_connection)
                return jsonify({'success': result}), 200
            else:
                return error_code({'error': 'C0002'})

        except Exception as error:
            return error_code({'error': 'A1043', 'programming_error': error})

        finally:
            try:
                db_connection.close()
            except Exception as error:
                return error_code({'error': 'A1043'})
