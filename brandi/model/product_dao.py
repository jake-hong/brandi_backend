import pymysql
from flask import jsonify 
import datetime

class ProductDao:
    """상품 모델
    Author : 김수정
    History: 
        2020-10-20: 초기생성
    """
    def get_product_list(self, db_connection, filter_dict):
        """
        조건에 맞는 상품의 목록을 반환합니다.
        Author : 김수정
        Args:
            sale        : 판매여부 (1 or 0)
            display     : 진열여부 (1 or 0)
            discount    : 할인여부 (1 or 0)
            seller_name : 셀러명 (korean_name)
            attribute   : 셀러속성 (id)
            product_number : 상품 번호 (id)
            product_name   : 상품 이름
            product_code   : 상품 코드 (option_id)
            from           : 상품 등록일 시작점
            until          : 상품 등록일 끝점
            seller_id      : 셀러의 account_id
        History: 
            2020-10-29: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            list_column_query = '''
            SELECT
                ps.id AS product_number,
                ps.created_at, 
                ps.name AS product_name, 
                ps.price,
                ps.discount_rate, 
                ps.is_displayed, 
                ps.is_on_sale, 
                (SELECT image_url FROM product_images pi WHERE ps.id = pi.product_id order by ordering asc limit 1) as image_url,
                sellers.korean_name AS seller_name, 
                seller_attributes.name AS attribute,
                (SELECT MIN(ops.id) FROM options ops WHERE ps.id=ops.product_id GROUP BY product_id) as product_code 
            ''' 

            count_column_query = '''
            SELECT
                count(0) as total_count
            '''

            join_query = '''
            FROM products ps 
            JOIN sellers ON ps.seller_id=sellers.account_id
            JOIN seller_attributes ON sellers.attribute_id=seller_attributes.id
            WHERE
                ps.is_deleted=0
            '''
            
            # 판매여부
            if filter_dict.get('sale', None) in ('0', '1'):
                join_query += ' AND ps.is_on_sale=%(sale)s'

            # 진열여부
            if filter_dict.get('displayed', None) in ('0', '1'):
                join_query += ' AND ps.is_on_sale=%(displayed)s'

            # 상품명
            if filter_dict.get('product_name', None):
                join_query += " AND ps.name=%(product_name)s"

            # 상품번호 (product_id)
            if filter_dict.get('product_number', None):
                join_query += ' AND ps.id=%(product_number)s'

            # 상품코드 (옵션번호)
            if filter_dict.get('product_code', None):  
                join_query += ' AND ops.id=%(product_code)s' 

            # 할인여부 
            # 할인
            if filter_dict.get('discount', None) == '1':
                join_query += ' AND ps.discount_rate > 0'
                
            # 미할인
            if filter_dict.get('discount', None) == '0':
                join_query += " AND ps.discount_rate IS NULL"
            
            # 날짜
            product_from  =  filter_dict.get('from', None)
            product_until =  filter_dict.get('until', None)

            # 시작일 정한경우
            if product_from:
                from_datetime = datetime.datetime(int(product_from[:4]), int(product_from[5:7].zfill(2)), int(product_from[8:10].zfill(2)))
                join_query += f" AND ps.created_at >= '{from_datetime}'"

            # 종료일 정한경우
            if product_until:
                until_datetime = datetime.datetime(int(product_until[:4]), int(product_until[5:7].zfill(2)), int(product_until[8:10].zfill(2)))
                join_query += f" AND ps.created_at <= '{until_datetime}'"

            # 셀러가 로그인 했을 때 : seller_id 직접 검색
            if filter_dict.get('seller_id', None):
                join_query += ' AND sellers.account_id = %(seller_id)s'
            
            # 마스터가 로그인 했을 때
            else:
                # 셀러 속성 
                if filter_dict.get('attribute', None):
                    join_query += ' AND sellers.attribute_id=%(attribute)s'

                # 셀러 이름 
                if filter_dict.get('seller_name', None):
                    print('이름 옴!')
                    join_query += " AND sellers.korean_name=%(seller_name)s"
            
            # Offset
            offset = int(filter_dict.get('offset', '0'))
            pagination = f" AND ps.id > {offset}"

            # limit
            limit = int(filter_dict.get('limit', '10'))
            pagination += f" limit {limit}"

            cursor.execute(list_column_query+join_query+pagination, filter_dict)
            list_row = cursor.fetchall()

            cursor.execute(count_column_query+join_query, filter_dict)
            count_row = cursor.fetchone()

            return list_row, count_row.get('total_count') if count_row else None
    
    def check_availability(self, db_connection, product_ids):
        """
        상품의 판매여부, 삭제여부를 반환합니다.
        Author : 김수정
        Args:
            product_id : {'product_ids': value}
                - value 1 ) INT
                - value 2 ) List
        Returns:
            db_connection   : DB
            id              : 상품 id
            is_on_sale      : 판매여부
            is_deleted      : 삭제여부
            price           : 가격
            discount_rate   : 할인율
            seller_id       : 셀러의 account_id
        History: 
            2020-10-29: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = '''
            SELECT  
                id,
                is_on_sale,
                is_deleted,
                price,
                discount_rate,
                seller_id
            FROM products
            WHERE  
            '''
            if type(product_ids.get('product_ids')) == int:
                query += 'products.id = %(product_ids)s'
                cursor.execute(query, product_ids)
                row = cursor.fetchone()

            else:
                query += 'products.id IN %(product_ids)s'
                cursor.execute(query, product_ids)
                row = cursor.fetchall()

            return row if row else False

    def get_colors(self, db_connection, body):
        """
        선택한 상품의 모든 색상 정보를 불러옵니다.
        Args:
            db_connection : db_connection
            product_id    : 선택한 상품 번호
        Returns:
            color       : 색상명
            color_id    : 색상 id
        Author : 김수정
        History: 
            2020-10-31: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = '''
            SELECT DISTINCT
                colors.name AS color,
                colors.id AS color_id
            FROM options
            JOIN colors ON options.color_id=colors.id
            WHERE  
                options.is_deleted=0
                AND options.product_id=%(product_id)s
            '''
            cursor.execute(query, body)
            row = cursor.fetchall()
            return row if row else None

    def get_sizes(self, db_connection, body):
        """
        선택한 상품의 모든 사이즈 정보를 불러옵니다.
        Args:
            db_connection : db_connection
            product_id    : 선택한 상품 번호
        ReturnsL
            size        : 사이즈명
            size_id     : 사이즈 id
        Author : 김수정
        History: 
            2020-10-31: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = '''
            SELECT DISTINCT
                sizes.name AS size,
                sizes.id AS size_id
            FROM options
            JOIN sizes ON options.size_id=sizes.id
            WHERE  
                options.is_deleted=0
                AND options.product_id=%(product_id)s
            '''
            cursor.execute(query, body)
            row = cursor.fetchall()
            return row if row else None
    
    def check_option(self, db_connection, body):
        """
        선택한 옵션과 수량을 확인하여 구매 가능여부를 반환합니다. 
        Args:
            db_connection : db_connection
            product_id    : 상품 번호
            size_id       : 사이즈 번호
            color_id      : 색상 번호
            quantity      : 구매 수량
        Returns:
            product_name            : 상품명
            option_id               : 선택한 option 의 id
            is_stock_controlled     : 옵션의 재고관리여부
            stock_quantity          : 옵션의 재고수량(관리할 경우)
        Author : 김수정
        History: 
            2020-10-31: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = '''
            SELECT  
                products.name AS product_name,
                options.id AS option_id,
                options.is_stock_controlled,
                options.stock_quantity
            FROM options
            JOIN products on options.product_id=products.id
            WHERE  
                options.is_deleted=0
                AND options.product_id=%(product_id)s
                AND size_id=%(size_id)s
                AND color_id=%(color_id)s
                AND products.min_quantity <= %(quantity)s  
                AND products.max_quantity >=%(quantity)s
            '''
            cursor.execute(query, body)
            row = cursor.fetchone()
            return row if row else None

    def get_all_product_for_seller(self, db_connection, body):
        """
        매출통계를 위해 로그인한 셀러의 전체 상품을 반환합니다.
        Args:
            db_connection : db_connection
            account_id    : seller 의 account_id
        Returns:
            id              : 상품의 id
            is_on_sale      : 판매여부
            is_displayed    : 진열여부
            is_deleted      : 삭제여부
        Author : 김수정
        History: 
            2020-11-01: 초기생성
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT 
                products.id,
                products.is_on_sale,
                products.is_displayed,
                products.is_deleted
            FROM 
                products
            WHERE 
            seller_id=%(account_id)s
            """
            cursor.execute(query, body)
            row = cursor.fetchall()

            return row if row else None                                                                          

    def change_product_status(self, db_connection, body):
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            """
            조건에 따라 상품의 상태(판매/진열)를 변경하고 변경자 id 를 저장합니다. 
            Args:
                db_connection : db_connection
                product_ids   : 변경할 상품들의 product_id
                updater_id    : 변경자(로그인 한 사람)의 account_id
                body          : 원하는 변경 상태dictionary
                    keys : "sales", "displayed" 
                    values : 1 or 0 
            Returns:
                ()
            Author : 김수정
            History: 
                2020-11-01: 초기생성
            """

            query = """
            UPDATE 
                products
            SET 
                updater_id=%(updater_id)s
            """            
            if body.get('sales', None) in (0,1):
                query += ", is_on_sale=%(sales)s"

            if body.get('displayed', None) in (0,1):
                query += ", is_displayed=%(displayed)s"

            query += " WHERE id IN %(product_ids)s"

            cursor.execute(query, body)
            result = cursor.fetchall()

            return result