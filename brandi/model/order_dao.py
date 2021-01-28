import pymysql
from flask import jsonify


class OrderDao:
    def save_receiver_info(self,
                           db_connection,
                           body
                           ):
        """
        구매자 정보를 저장하고 저장된 아이디 값을 반환합니다. 
        Args:
            db_connection  : db_connection
            body           : 딕셔너리
                buyer_name     : 수령인 이름
                contact        : 수령인 전화번호
                zip_code       : 수령지 우편번호
                street_address : 수령지 주소
                detail_address : 수령지 상세주소}
        Return:
            MAD(id) : 수령인의 id
        Author : 김수정
        History: 
            2020-10-31: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            insert_query = '''
            INSERT INTO receivers(
                name, 
                contact, 
                zip_code, 
                street_address, 
                detail_address
                )
            VALUES(
                %(buyer_name)s,
                %(contact)s,
                %(zip_code)s,
                %(street_address)s,
                %(detail_address)s
            )
            '''
            cursor.execute(insert_query, body)
            row = cursor.lastrowid

            return row if row else None

    def make_order_info(self, db_connection, body):
        """
        orders 테이블에 가격과 수령자 정보를 저장하고 생성된 주문 번호를 반환합니다.
        Args:
            db_connection : db_connection
            receiver_id   : 주문자 번호
            total_price   : 총 결제 금액
        Returns:
            MAX(id) : 생성된 주문의 id
        Author : 김수정
        History: 
            2020-10-31: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            insert_query = '''
            INSERT INTO orders(receiver_id, total_paied_price)
            VALUES(
                %(receiver_id)s,
                %(total_price)s
            )
            '''
            cursor.execute(insert_query, body)
            row = cursor.lastrowid

            return row if row else None

    def make_detail_order_info(self, db_connection, body):
        """상세 주문정보를 저장합니다.
        Args:
            db_connection : db_connection
            body          : 딕셔너리
                {order_id      : 직전에 생성된 주문번호
                product_id    : 상품번호
                seller_id     : 셀러 번호
                receiver_id   : 주문자 번호
                option_id     : 옵션 번호
                price         : 상품의 현재 가격
                discount_rate : 상품의 현재 할인율
                quantity      : 구매한 수량}
        Author : 김수정
        History: 
            2020-10-31: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = '''
            INSERT INTO detail_orders(
                order_id,      
                product_id,      
                seller_id,       
                receiver_id,     
                option_id,
                price,           
                discount_rate,   
                quantity,
                status_id)        
            VALUES(
                %(order_id)s,
                %(product_id)s,
                %(seller_id)s,
                %(receiver_id)s,
                %(option_id)s,
                %(price)s,
                %(discount_rate)s,
                %(quantity)s,
                (SELECT id FROM detail_order_statuses WHERE name='상품준비')
            )
            '''
            cursor.execute(query, body)

            row = cursor.fetchone()

    def make_change_to_stock(self, db_connection, body):
        """
        재고 수량을 업데이트 합니다.
        Args:
            db_connection : db_connection
            body          : 딕셔너리
                {option_id     : 재고 수량 변경할 옵션 번호
                quantity      : 재고 수량에서 제할 구매수량}
        Author : 김수정
        History: 
            2020-10-31: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = '''
            UPDATE options SET stock_quantity -= %(quantity)s
            WHERE id=%(option_id)s
            '''
            cursor.execute(query, body)
            row = cursor.fetchone()

    def get_one_month_orders(self, db_connection, body):
        """
        조회일시로부터 지난 한 달동안 생성된 주문정보를 반환합니다.
        Args:
            db_connection : db_connection
            body          : 딕셔너리
                {account_id    : seller 의 account id
                last_month    : 1달 전 datetime}
        Returns:
            order_id      : 주문의 id
            price         : 주문시의 상품 단가
            ordered_at    : 주문일시
            discount_rate : 주문시의 할인율 (ex. 15% 할인일 경우 0.85)
        Author : 김수정
        History: 
            2020-11-01: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT 
                order_id,
                price,
                ordered_at,
                quantity,
                discount_rate,
                detail_order_statuses.name AS status_name
            FROM detail_orders
            JOIN detail_order_statuses ON detail_orders.status_id=detail_order_statuses.id
            WHERE seller_id=%(account_id)s
                AND ordered_at >= (SELECT DATE_ADD((SELECT TIMESTAMP(CURDATE())), INTERVAL -29 DAY))
            """
            cursor.execute(query, body)
            row = cursor.fetchall()

            return row if row else None

    def get_orders_to_confirm(self, db_connection, body):
        """
        10분 이상 된 모든 배송완료 주문을 반환합니다. 
        Args:
            db_connection : db_connection
            ten_m_before  : 지금으로부터 10분 전
            status_id     : 조회할 주문의 현 상태 id (배송 완료-6)
        Returns:
            id              : detail_order 의 id
            product_name    : 주문한 상품명
            receiver_name   : 수령인 이름
        Author : 김수정
        History: 
            2020-11-02: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT 
                detail_orders.id,
                products.name AS product_name,
                receivers.name AS receiver_name
            FROM detail_orders
            JOIN detail_order_statuses ON detail_orders.status_id=detail_order_statuses.id
            JOIN products ON detail_orders.product_id=products.id
            JOIN receivers ON detail_orders.receiver_id=receivers.id
            WHERE detail_order_statuses.id=%(status_id)s
                AND detail_orders.ordered_at <= DATE_ADD(NOW(), INTERVAL -%(minutes)s MINUTE)
            """
            cursor.execute(query, body)
            row = cursor.fetchall()

            return row if row else None

    def confirm_order_delivery(self, db_connection, body):
        """
        detail_order 의 status 를 "구매확정" 으로 변경합니다. 
        Args:
            db_connection : db_connection
            order_ids     : 변경할 detail_order 들의 id
            status_id     : 변경 한 이후의 상태의 id
        Author : 김수정
        History: 
            2020-11-02: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            UPDATE 
                detail_orders
            SET status_id=%(status_id)s
            WHERE detail_orders.id IN %(order_ids)s
            """
            cursor.execute(query, body)
            row = cursor.fetchall()

    def log_order_confirm_history(self, db_connection, body):
        """
        scheduler 로 구매 확정시킨 내역을 기록합니다.         
        Args:
            db_connection : db_connection
            order_ids     : 주문상태 변경 내역을 기록할 detail_order 들의 id
            status_id     : 변경 된(after) 상태의 id
        Author : 김수정
        History: 
            2020-11-02: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            INSERT INTO detail_order_status_log(
                status_id,
                detail_order_id,
                updater_id
            ) VALUES(
                %(status_id)s,
                %(order_id)s,
                %(account_id)s
            )
            """
            for order_id in body['order_ids']:
                body['order_id'] = order_id
                row = cursor.execute(query, body)
                row = cursor.fetchone()

    def check_order_status(self, db_connection, body):
        """
        선택한 주문들의 현재 상태를 확인합니다.     
        Args:
            db_connection : db_connection
            body
        Author : 김수정
        History: 
        #     2020-11-02: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT 
                id 
            FROM 
                detail_orders 
            WHERE
                status_id=%(status_id)s
                AND id IN %(id)s
            """

            cursor.execute(query, body)
            row = cursor.fetchall()

        return row

    def check_order_flow(self, db_connection, body):
        """
        주문 상태 변경시, 어떤 상태로 변경할지 이름과 id 를 리턴해 줍니다.   
        Args:
            db_connection : db_connection
            body
        Returns:
            id      : 바꾼 이후에 가질 상태 id
            name    : 바꾼 이후에 가질 상태 이름
        Author : 김수정
        History: 
        #     2020-11-02: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT 
                id,
                name 
            FROM 
                detail_order_statuses 
            WHERE id = 
                (
                SELECT 
                    after_id 
                FROM  
                    detail_order_statuses 
                JOIN  
                    order_actions ON detail_order_statuses.id=order_actions.before_id 
                WHERE 
                    order_actions.before_id=%(status_id)s
                ); 
            """
            row = cursor.execute(query, body)
            row = cursor.fetchone()

        return row

    def get_order_info(self, db_connection, body):
        """
        주문 상태 변경후, 슬랙으로 보낼 구매자명과 상품명을 조회하여 반환합니다.   
        Args:
            db_connection : db_connection
            body          : 딕셔너리
                {
                    id  : 리스트, detail_orders 의 id들
                }
        Returns:
            id              : 바꾼 이후에 가질 상태 id
            receiver_name   : 주문자 이름
            product_name    : 주문한 상품명
        Author : 김수정
        History: 
        #     2020-11-02: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT
                detail_orders.id,
                receivers.name as receiver_name,
                products.name as product_name
            FROM 
                detail_orders
            JOIN 
                receivers ON detail_orders.receiver_id=receivers.id
            JOIN
                products ON detail_orders.product_id=products.id
            WHERE 
                detail_orders.id IN %(id)s
            """
            row = cursor.execute(query, body)
            row = cursor.fetchall()

            return row

    def get_complete_order_list(self, order_info, db_connection):
        """주문 관리 목록을 보내줍니다.
        Args:
            db_connection : db_connection
        Returns:
            주문 관리 리스트   
        Author : 홍성은
        History: 
            2020-11-03: 초기생성
            2020-11-04: 페이지네이션 추가 
        """

        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT
                DATE_FORMAT(o.paied_at,'%%Y-%%m-%%d %%H:%%m:%%s') AS a_paied_at,
                d.order_id as b_oreder_id,
                p.name as d_products_name,
                d.id as c_detail_order_id,
                d.quantity as f_quantity,
                d.option_id as e_option_id,
                r.contact as h_reciever_contact,
                r.name as g_reciever,
                dos.name as i_detail_order_statuses_name
            FROM 
                detail_orders AS d
            JOIN
                orders AS o ON d.order_id = o.id
            JOIN 
                products AS p ON d.product_id = p.id
            JOIN 
                sellers AS s ON d.seller_id = s.id 
            JOIN
                receivers AS r ON d.receiver_id = r.id
            JOIN
                detail_order_statuses AS dos ON dos.id = d.status_id    
            """
            # 주문관리 카테고리가 바뀌는 경우
            if order_info['status_id']:
                query += """
                WHERE d.status_id=%(status_id)s
                """

            # 주문번호에 따른 필터
            if order_info['order_number']:
                query += """
                AND o.id = %(order_number)s
                """
            # 상세주문번호에 따른 필터
            if order_info['detail_order_id']:
                query += """
                AND d.id = %(detail_order_id)s
                """
            # 주문자명에 따른 필터
            if order_info['receiver_name']:
                query += """
                AND r.name = %(receiver_name)s
                """
            # 핸드폰 번호에 따른 필터
            if order_info['phone_number']:
                query += """
                AND r.contact = %(phone_number)s
                """

            # 상품명에 따른 필터
            if order_info['product_name']:
                query += """
                AND p.name = %(product_name)s
                """

            query += """
            ORDER BY 
                order_id 
            DESC 
            LIMIT 
                %(limit)s
            OFFSET
                %(offset)s
            """
            cursor.execute(query, order_info)
            order = cursor.fetchall()

            return order
