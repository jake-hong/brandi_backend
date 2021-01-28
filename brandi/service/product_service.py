from flask import request, jsonify

from model.product_dao import ProductDao
from model.account_dao import AccountDao

from utils import error_code

product_dao = ProductDao()
account_dao = AccountDao()

class ProductService():
    def get_product_list(self, db_connection, filter_dict):
        """
        상품 목록 보기
        Args:
            db_connection : querystring 에 담긴 필터 정보
            filter_dict   : Query string 으로 전달받은 필터들
        Returns:
            {'success' : final_result } : 최종 리스트 반환
            {'success' : None } : 해당되는 상품 없음
        Authors: 김수정
        History:
        2020-10-29 : 초기 생성
        """
        try:
            # 마스터인지 셀러인지 파악하기
            account_id = request.account_id
            is_master = account_dao.check_master(db_connection, {'account_id':account_id})
            
            # 셀러인 경우
            if not is_master:
                # ImmutableMultiDict 를 MultiDict 로 바꿔줌
                filter_dict = filter_dict.copy() 
                # 필터 딕셔너리에 셀러 아이디를 추가해줌
                filter_dict['seller_id'] = account_id

            # 해당되는 모든 상품을 가져옴
            filtering_result, total_count = product_dao.get_product_list(db_connection, filter_dict)
            for product in filtering_result:
                created_at_datetime = product['created_at'] 
                year, month, day = created_at_datetime.year, str(created_at_datetime.month).zfill(2), str(created_at_datetime.day).zfill(2)
                product['created_at'] = f'{year}-{month}-{day}'

            # 해당하는 상품이 없는 경우
            if not filtering_result:
                return {'success': {'data':None, 'total_product':0}}
            
            # 상품이 있는 경우
            else: 
                """
                for product in filtering_result:
                    datetime_format = product['created_at'] 
                    str_month = datetime_format.year
                    str_day = datetime_format.day

                    transfer_format = f'{datetime_format.year}-{str_month}-{str_day}'
                """
                return {'success': {'data':filtering_result, 'total_product':total_count}}

        except (KeyError, TypeError) as error:
            return {'error':"C0001", 'programming_error':error}

    def get_options_service(self, db_connection, product_id):
        """주문을 위해 선택한 상품의 옵션정보를 불러옵니다.
        Args:
            db_connection : db_connection
            product_id    : 선택한 상품 번호
        Returns:
            {'success' : None } : 해당되는 상품 없음 ###
        Authors: 김수정
        History:
        2020-10-31 : 초기 생성
        """
        try:
            # 있는 상품인지 확인

            is_product_available = product_dao.check_availability(db_connection, {'product_ids':product_id})

            # 존재하지 않는 상품인 경우
            if not is_product_available:
                return {'error':'P2011'}
            
            # 존재하는 상품의 경우
            else:
                # 삭제된 상품
                if is_product_available['is_deleted']:
                    return {'error':'P2012'}

                # 미판매 상품
                elif is_product_available['is_on_sale'] == False:
                    return {'error':'P2013'}
                
                else:

                    color_list = product_dao.get_colors(db_connection, {'product_id':product_id})
                    size_list = product_dao.get_sizes(db_connection, {'product_id':product_id})

                    # 옵션이 없는 경우 - 구매 불가
                    if not color_list or not size_list:

                        return {'error':'P2014'}

            return {'success': {'colors':color_list, 'sizes':size_list}}

        except (KeyError, TypeError) as error:
            return {'error':"C0001", 'programming_error':error}

    def change_status(self, db_connection, body):
        """선택한 상품들의 판매여부, 진열여부를 변경합니다.
        Args:
            db_connection : db_connection
            body          : 딕셔너리
                {
                displayed : 0 or 1 
                sales     : 0 or 1 
                product_ids : [상품 번호들]
                }
        Returns:
            {'success' : None } : 해당되는 상품 없음 
        Authors: 김수정
        History:
        2020-10-31 : 초기 생성
        """
        product_ids = body['product_ids']

        # 있는 상품인지 확인
        products_to_change = product_dao.check_availability(db_connection, {'product_ids':product_ids})
        
        # 없는 상품 포함된 경우
        if len(products_to_change) != len(product_ids):
            return {'error':'P2011'}

        updater_id  = request.account_id
        body['updater_id'] = updater_id
        body['product_ids'] = product_ids

        # 상품이 잘 있는 경우, 상품 상태 바꿔줌
        change_result = product_dao.change_product_status(
                db_connection, 
                body
            )

        return {'success': "변경 완료"}