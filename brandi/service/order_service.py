from flask import request, jsonify

from model.product_dao import ProductDao
from model.account_dao import AccountDao
from model.order_dao   import OrderDao

from utils import error_code, send_slack

product_dao = ProductDao()
account_dao = AccountDao()
order_dao   = OrderDao()

class OrderService():
    def make_order_service(self, db_connection, product_id, body):
        """
        주문을 생성하기 위해 상품정보, 옵션정보, 수령인 정보를 확인하고 저장합니다.
        Args:
            db_connection : db_connection
            product_id    : 선택한 상품 번호
            body          : 색상, 사이즈, 수량, 수령인 정보, 수령지 정보
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
                if is_product_available['is_deleted'] == 1:
                    return {'error':'P2012'}
                # 미판매 상품
                elif is_product_available['is_on_sale'] == 0:
                    return {'error':'P2013'}
                else:
                    # 옵션 & 수량 정보 확인하기 
                    # - 사이즈와 컬러를 넣어서 옵션이 있나 확인)
                    # - 구매 수량이 상품의 최대/최소 구매 수량에 맞는지)
                    body['product_id'] = product_id
                    option_info = product_dao.check_option(
                        db_connection, 
                        body
                        )

                    # 옵션이나 수량이 없으면 - 없는 거라고 리턴
                    if not option_info:
                        return {'error':'P2014'}

                    # 옵션과 최소/최대 수량정보는 알맞으나 재고가 없는 경우
                    if option_info['is_stock_controlled']:
                        if option_info['stock_quantity'] < body['quantity']:
                            return {'error':'P2015'}

                    # 주문을 생성함
                    # 가격을 확인함 
                    price = is_product_available['price']
                    if is_product_available['discount_rate']:
                        discount_rate = (1-is_product_available['discount_rate']*0.01)
                    else:
                        discount_rate = 1
                    quantity = body['quantity']

                    total_price = price*discount_rate*quantity
                    
                    # 우선 주문자 정보를 저장하고 id를 받음
                    # print(body)
                    receiver_id = order_dao.save_receiver_info(
                        db_connection, 
                        body
                    )

                    # order 만들기
                    order_id = order_dao.make_order_info(db_connection, {'receiver_id':receiver_id, 'total_price':total_price})

                    # detail order 에 전달할 딕셔너리 생성
                    detail_body = {}
                    detail_body['order_id'] = order_id
                    detail_body['product_id'] = product_id
                    detail_body['seller_id'] = is_product_available['seller_id']
                    detail_body['receiver_id'] = receiver_id
                    detail_body['price'] = price
                    detail_body['discount_rate'] = discount_rate
                    detail_body['quantity'] = quantity

                    # detail order 만들기
                    option_id = option_info['option_id']
                    detail_body['option_id'] = option_id
                    order_make = order_dao.make_detail_order_info(db_connection, detail_body)

                    # 재고 수량 관리하는 경우 재고량 수정해줌
                    if option_info['is_stock_controlled']:
                        stock_control_result = order_dao.make_change_to_stock(db_connection, detail_body)
            
            send_slack(body['buyer_name'], option_info['product_name'], '상품준비')
            return {'success': '구매가 완료 되었습니다.'}

        except (KeyError, TypeError) as error:
            return {'error':"C0001", 'programming_error':error} 

    def make_order_progress(self, db_connection, account_id, body):
        """
        선택한 주문의 배송상태를 확인하고 요청받은 대로 변경합니다. 
        Args:
            db_connection : db_connection
            account_id    : 로그인한 유저의 id
            body          : 
                {id         : detail_order 의 id 들 (list), 
                status_id   : 현재 status 의 id}
        Returns:
            {'success':"변경 완료"}
            {'error':'O3011'} - 주문이 존재하지 않거나, 주문상태와 요청이 맞지 않는 경우 (ex. 배송중인데 구매확정으로 변경하는 경우 등)
        Authors: 김수정
        History:
        2020-11-04 : 초기 생성
        """
        try:
            # 주문들의 현재 상태를 확인합니다. 
            orders_status = order_dao.check_order_status(db_connection, body)
            
            # 현재 상태와 변경 원하는 상태가 맞지 않는 경우
            if len(orders_status) != len(body['id']):
                return {'error':'O3011'}
            
            # 맞는 경우
            else:
                # 변경하고자 하는 상태의 id 를 가져옴 (after_status의 id)
                after_status_info = order_dao.check_order_flow(db_connection, body)

                # 변경하기 위해 body 에 담아줌
                body['status_id']  = after_status_info['id']
                body['order_ids']  = body['id']
                body['account_id'] = account_id

                # 상태 변경
                changed_orders = order_dao.confirm_order_delivery(db_connection, body)
                # 상태 변경한 시간을 담아와서 기록 남길떄 시간을 넣어주는 게 좋을지???
                # 기록 남김
                history = order_dao.log_order_confirm_history(db_connection, body)
                
                #슬랙 보내기 위해 받는이와 상품정보 가져옴
                order_info = order_dao.get_order_info(db_connection, body)

                # 개별 주문에 대한 받는이와 상품정보를 포함하여 슬랙 보내줌
                status_name = after_status_info['name']
                for order in order_info:
                    buyer_name = order['receiver_name']
                    product_name = order['product_name']
            
                    send_slack(buyer_name, product_name, status_name) 
                
                return {'success':"변경 완료"}

        except (KeyError, TypeError) as error:
            return {'error':"C0001", 'programming_error':error} 
    
    def get_complete_order(self,order_info, db_connection):
        """
        결제완료된 리스트 가져오기 
        Args: 
            order_info: 결제 리스트
            db_connection: 연결된 db
        Returns: 
            주문 리스트
        Authors: 
            홍성은 
        History:
            2020-11-03: 초기 생성 
        """
        if order_info is None:
            return error_code({'error':'C0006'})
        result = order_dao.get_complete_order_list(order_info,db_connection=db_connection)
        return result 