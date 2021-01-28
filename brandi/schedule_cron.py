import datetime
import pymysql

from flask  import Flask
from app    import create_app

from connection         import get_connection
from utils              import send_slack, error_code
from model.order_dao    import OrderDao
    
app = Flask(__name__)
order_dao = OrderDao()

@app.route("/")   
def confirm_order(m): 
    """   
    10분 이상 된 detail_order 의 status 를 "구매확정" 으로 변경합니다. 
    Args: 
        db_connection : db_connection 
        m             : n분 (우선 10분)   
    Author : 김수정   
    History:  
        2020-11-02: 초기생성  
    """   
    # DB Connection   
    try:
        db_connection = get_connection()

        # detail order statuses
            status_id_list = {
                1: '결제완료',
                6: '구매확정',
                5: '배송완료',
                3: '배송준비',
                4: '배송중',
                2: '상품준비',
            }

        orders_to_confirm = order_dao.get_orders_to_confirm(
            db_connection,    
            {'minutes':m, # 함수의 변수로 주어진 시간(분 단위)
            'status_id':status_id_list['배송완료']}
            ) 
        
        # 주문이 있는 경우, 해당 주문들의 배송상태를 구매확정(6)으로 변경
        if orders_to_confirm: 
            order_ids = [order['id'] for order in orders_to_confirm]
            order_body =  {'order_ids':order_ids, 'status_id':status_id_list['구매확정'], 'account_id':1}
            order_dao.confirm_order_delivery(db_connection, order_body)

            # 변경 내역을 저장    
            order_dao.log_order_confirm_history(db_connection, order_body)
            db_connection.commit()

            # 슬랙 보냄   
            for order in orders_to_confirm:   
                buyer_name = order['receiver_name']
                product_name = order['product_name']
                send_slack(buyer_name, product_name, "구매확정")

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

confirm_order(1)