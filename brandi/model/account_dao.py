import pymysql
from flask import jsonify


class AccountDao:
    """계정 모델 
    Authors:홍성은
    History: 2020-10-27: 초기생성
    """

    def login_account(self, db_connection, body):
        """
        입력한 아이디를 조회하여 id 와 비밀번호를 반환합니다.
        Author: 김수정
        Args:
            identification : 사용자가 입력한 로그인용 아이디
        Returns:
            id,
            password
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = '''
            SELECT id, password FROM accounts
            where identification = %(identification)s
            '''
            cursor.execute(query, body)
            row = cursor.fetchone()
            print(row)
            return row if row else None

    def is_seller_not_validated(self, db_connection, body):
        """
        입점대기 유저의 로그인을 막기 위해 셀러 상태를 확인합니다.
        Authors: 김수정
        Args: 
            db_connection : db
            account_id : 로그인한 유저의 id
        Returns:
            account_id      : 셀러의 account_id
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = '''
            SELECT account_id
            FROM sellers
            JOIN seller_statuses ON sellers.status_id=seller_statuses.id
            WHERE account_id=%(account_id)s AND seller_statuses.name='입점대기'
            '''
            cursor.execute(query, body)
            row = cursor.fetchone()

            return row if row else False

    def check_master(self, db_connection, body):
        """
        Master 계정인지 확인하여 이름과 id 를 반환합니다. 
        Authors: 김수정
        Args: 
            db_connection : db
            account_id : 로그인한 유저의 id
        Returns:
            id      : master.id
            name    : master.name 
            False   : master 가 아닌 경우
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = '''
            SELECT id, name
            FROM masters
            WHERE account_id=%(account_id)s
            '''
            cursor.execute(query, body)
            row = cursor.fetchone()

            return row if row else False

    def get_general_info(self, db_connection, body):
        """
        선택한 셀러의 정보를 sellers 테이블에서 불러옵니다. 
        Authors: 김수정
        Args: 
            db_connection : db
            seller_id : 로그인한 유저의 id
        Returns:
            딕셔너리 형태로 반환
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = '''
                SELECT  accounts.id as seller_id,   
                        thumbnail_url,         
                        seller_statuses.name AS status,        
                        identification,        
                        email,                 
                        korean_name,        
                        seller_attributes.name AS attribute,     
                        background_image_url,  
                        introduction,          
                        description,           
                        cs_contact,            
                        cs_from,          
                        cs_until,         
                        cs_weekend_from,          
                        cs_weekend_until,         
                        zip_code,              
                        address,               
                        detail_address,
                        refund_info,
                        shipment_info 
                FROM sellers 
                    JOIN seller_statuses ON sellers.status_id = seller_statuses.id 
                    JOIN accounts ON sellers.account_id = accounts.id 
                    JOIN seller_attributes ON sellers.attribute_id=seller_attributes.id 
                WHERE accounts.id = %(seller_id)s
            '''
            cursor.execute(query, body)
            result = cursor.fetchone()

            return result if result else None

    def get_status_log(self, db_connection, body):
        """
        선택한 셀러의 입점상태 변경 기록을 불러옵니다. 
        Authors: 김수정
        Args: 
            db_connection : db
            seller_id : 셀러의 account_id
        Returns:
            status     : 변경 후 상태 이름
            changed_at : 변경일시
            updated_by : 변경했던 마스터의 이름
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = '''
            SELECT   
                seller_statuses.name AS status, 
                changed_at,  
                m.identification AS updated_by 
            FROM seller_status_log    
                JOIN seller_statuses ON seller_status_log.changed_status_id = seller_statuses.id 
                LEFT JOIN accounts AS m ON seller_status_log.updater_id = m.id                  
                JOIN accounts ON seller_status_log.seller_id = accounts.id 
            WHERE accounts.id = %(seller_id)s 
            '''
            cursor.execute(query, body)
            result = cursor.fetchall()
            result = result if result else None

            return {'seller_status_log': result}

    def get_manager_info(self, db_connection, body):
        """
        선택한 셀러의 담당자 정보를 managers 테이블에서 불러옵니다. 
        Authors: 김수정
        Args: 
            db_connection : db
            seller_id : 셀러의 account_id
        Returns:
            name     : 담당자 이름
            contact  : 담당자 전화번호
            ordering : 담당자 순서 (1~3)
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = '''
            SELECT   
                name,
                contact,
                email,
                ordering
            FROM managers
            WHERE seller_id = %(seller_id)s AND is_deleted=False 
            '''
            cursor.execute(query, body)

            result = cursor.fetchall()
            result = result if result else None

            return {'managers': result}

    def get_attributes(self, db_connection):
        """
        셀러 속성(마켓/쇼핑몰 등)의 리스트를 불러옵니다. 
        Authors: 김수정
        Args:       
            None
        Returns:
            category_id     : 속성의 id
            category_title  : 속성의 이름
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = '''
            SELECT   
                id AS category_id,
                name AS category_title
            FROM seller_attributes
            '''
            cursor.execute(query)
            result = cursor.fetchall()

            return {'attributes': result}

    def action_check(self, db_connection, body):
        """
        셀러의 상태 번호와 액션의 비포 번호를 비교하여 일치하는 경우 변경하고자하는 status_id 를 반환합니다.
        작성자: 김수정
        Args:
            db_connection : db
            body          : dictionary
                seller_id     : 상태 바꿔줄 셀러의 account_id
                action_id     : 취할 액션의 id (body)
        Returns:
            after_status_id : 해당 번호로 셀러 상태번호 변경
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = '''
            SELECT     
                ssa.after_status_id as after_status_id  
            FROM seller_statuses_actions AS ssa  
            JOIN actions AS a ON ssa.action_id=a.id  
            JOIN sellers AS s ON ssa.before_status_id=s.status_id  
            JOIN accounts AS acc ON s.account_id=acc.id  
            WHERE acc.id=%(seller_id)s AND a.id=%(action_id)s; 
            '''
            cursor.execute(query, body)
            result = cursor.fetchone()

            return result if result else None

    def action_change(self, db_connection, body):
        """
        셀러의 상태 번호를 변경하고, 이력 테이블에 열을 추가합니다.
        Authors: 김수정
        Args:
            db_connection : db
            body          : dictionary
                seller_id     : 상태 바꿔줄 셀러의 account_id
                action_id     : 액션의 id
                master_id     : 업데이트 한 마스터의 account_id
        Returns:
        """

        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query_update = '''
            UPDATE sellers 
            SET status_id=%(after_status_id)s
            WHERE account_id=%(seller_id)s
            '''
            cursor.execute(query_update, body)

            query_insert = '''
            INSERT INTO seller_status_log(
                changed_status_id,
                seller_id,
                updater_id
            ) VALUES(
                %(after_status_id)s,
                %(seller_id)s,
                %(master_id)s
            )
            '''
            cursor.execute(query_insert, body)
            result = cursor.lastrowid

            return result if result else None

    def get_navs(self, db_connection, is_master):
        """
        마스터/셀러 여부에 따라 네이게이션 바에 나타날 nav 정보를 불러옵니다.
        작성자: 김수정
        Args:
            db_connection : db
            is_master     : master 여부 (T/F)
        Returns:
            menu        : 네비게이션 바 이름
            menu_id     : 네비게이션 바 id
            sub_menu    : 네비게이션 바 누르면 나오는 것 이름
            sub_menu_id : 네비게이션 바 누르면 나오는 것 id
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = '''
            SELECT 
            menus.name AS menu,
            menus.id AS menu_id,
            sub_menus.name AS sub_menu,
            sub_menus.id AS sub_menu_id
            FROM menu_sets_account_types
            JOIN menu_sets ON menu_sets_account_types.menu_set_id=menu_sets.id 
            JOIN menus ON menu_sets.menu_id=menus.id 
            JOIN sub_menus ON menu_sets.sub_menu_id=sub_menus.id 
            JOIN account_types ON menu_sets_account_types.account_type_id=account_types.id
            WHERE account_types.name=%s
            '''
            master_or_seller = 'master' if is_master else 'seller'

            cursor.execute(query, master_or_seller)

            result = cursor.fetchall()
            result = result if result else None

            return result

    def check_identification(self, seller_info, db_connection):
        """회원가입 시 identificaion 중복 체크 
        Args: 
            seller_info: controller에서 받은 셀러정보 변수
            db_connection: DB 커넥션 변수
        Returns: 
            identification service로 전달  
        Authors: 홍성은
        History:
            2020-10-26 : 초기 생성
            2020-10-27~28 : 오류, SQL 수정 
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT 
                identification  
            FROM 
                accounts
            WHERE 
                identification = %(seller_info)s
            """
            cursor.execute(query, {'seller_info': seller_info})
            # 조회된 결과 중 데이터 1개 반환
            result = cursor.fetchone()
            return result

    def signup_account(self, seller_info, db_connection):
        """회원가입시 전달된 데이터 입력  
        Args: 
            seller_info: controller에서 받은 셀러정보 변수
            db_connection: DB 커넥션 변수
        Returns: 
            identification service로 전달  
        Authors: 홍성은
        History:
            2020-10-26 : 초기 생성
            2020-10-27~28 : 오류, SQL 수정 
            2020-11-04 : insert_sellers,insert_managers 매소드 분리 했을 때 커밋에 문제가 생겨 
                         lastrowid를 사용하여 signup_account 메소드로 합침.
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            insert_accounts_query = """
            INSERT INTO accounts(
                identification,
                password,
                account_type_id
            )VALUES(
                %(identification)s,
                %(password)s,
                2
            )
            """
            # SQL문 실행 및 기입
            # account 정보 기입
            cursor.execute(insert_accounts_query, seller_info)

            # 새롭게 생성된 id 값을 가져옴
            account_number = cursor.lastrowid
            seller_info['account_id'] = account_number

            insert_sellers_query = """
            INSERT INTO sellers(
                contact,
                account_id,
                attribute_id,
                status_id,
                korean_name,
                english_name,
                cs_contact,
                updater_id
            ) VALUES (
                %(contact)s,
                %(account_id)s,             
                %(attribute_id)s,
                1,
                %(korean_name)s,    
                %(english_name)s,
                %(cs_contact)s,
                (SELECT accounts.id FROM accounts JOIN sellers AS s ON accounts.id = s.account_id WHERE identification=%(identification)s)
            )
            """
            # 셀러 정보 기입
            cursor.execute(insert_sellers_query, seller_info)

            seller_account_no = cursor.lastrowid
            seller_info['seller_id'] = seller_account_no

            # 담당자 정보 생성
            insert_managers_query = """
            INSERT INTO managers(
                contact,
                seller_id,
                ordering,
                updater_id
            ) VALUES (
                %(contact)s,
                %(seller_id)s,
                1,
                (SELECT id FROM accounts WHERE identification=%(identification)s)
            )
            """
            cursor.execute(insert_managers_query, seller_info)

            return jsonify({"message": "SUCCESS"})

    def check_korean_name(self, korean_name, db_connection):
        """회원가입 시 korean_name 중복 체크 
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT 
                sel.id
            FROM 
                sellers AS sel
            WHERE 
                sel.korean_name=%(korean_name)s
            """

            cursor.execute(query, {'korean_name': korean_name})
            result = cursor.fetchone()
            return result

    def check_english_name(self, english_name, db_connection):
        """회원가입 시 english_name 중복 체크 
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT 
                sel.id
            FROM 
                sellers AS sel
            WHERE 
                sel.english_name=%(english_name)s
            """

            cursor.execute(query, {'english_name': english_name})
            result = cursor.fetchone()
            return result

    def check_cs_contact(self, cs_contact, db_connection):
        """회원가입 시 cs_contact 중복 체크 
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT 
                sel.id
            FROM 
                sellers AS sel
            WHERE 
                cs_contact=%(cs_contact)s
            """

            cursor.execute(query, {'cs_contact': cs_contact})
            result = cursor.fetchone()
            return result

    def get_seller_list(self, seller_list, db_connection):
        """셀러 리스트
            GET 한 셀러 리스트 return , 검색 필터로 검색 
            페이지네이션 offset, limit 값 받아서 구현 

        Args:
            filter_seller : 셀러 필터링
            db_connection : 연결된 DB

        Returns: 
            셀러 리스트

        Authors:
            홍성은 

        History:
            2020-10-27 : 셀러리스트 초기 생성
            2020-10-29 : 유효성 검사 추가 
            2020-10-31 : 셀러 검색 기능 추가
        """
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT 
                sel.id,
                a.id as account_id,
                a.identification,
                sel.english_name,
                sel.korean_name,
                m.name as manager_name,
                s.name as status_name,
                m.contact,
                m.email,
                at.name as attribute,
                DATE_FORMAT(sel.created_at,'%%Y-%%m-%%d %%H:%%m:%%s') AS created_at,
                s.id as status_id
            
            """

            total_seller_count = """
            SELECT
                count(*) as total_seller_count
            """

            join_query = """
            FROM 
                sellers AS sel
            JOIN 
                accounts AS a ON sel.account_id = a.id 
            LEFT JOIN 
                managers AS m ON sel.id = m.seller_id
            JOIN 
                seller_statuses AS s ON sel.status_id = s.id 
            JOIN 
                seller_attributes AS at ON sel.attribute_id = at.id
            WHERE 
                sel.id >= 1 AND s.id != 5
            """

            # 셀러 필터 기능, seller_list에 검색 키워드가 있는지 확인 후에 쿼리 추가.
            if seller_list['id']:
                join_query += """
                AND sel.id = %(id)s
                """

            if seller_list['identification']:
                join_query += """
                AND a.identification = %(identification)s
                """

            if seller_list['english_name']:
                join_query += """
                AND sel.english_name = %(english_name)s
                """

            if seller_list['korean_name']:
                join_query += """
                AND sel.korean_name = %(korean_name)s
                """

            if seller_list['manager_name']:
                join_query += """
                AND m.name = %(manager_name)s
                """
            if seller_list['status_name']:
                join_query += """
                AND s.name = %(status_name)s
                """

            if seller_list['contact']:
                join_query += """
                AND m.contact = %(contact)s
                """

            if seller_list['email']:
                join_query += """
                AND m.email = %(email)s
                """

            if seller_list['attribute']:
                join_query += """
                AND at.name = %(attribute)s
                """

            start_date = seller_list['start_date']
            end_date = seller_list['end_date']

            if seller_list['start_date'] and seller_list['end_date']:
                seller_list['start_date'] = start_date + ' 00:00:00'
                seller_list['end_date'] = end_date + ' 23:59:59'
                join_query += """
                AND sel.created_at > %(start_date)s 
                AND sel.created_at < %(end_date)s

                """

            pagination_query = """
            ORDER BY 
                sel.id 
            DESC 
            LIMIT 
                %(limit)s 
            OFFSET
                %(offset)s
            """

            cursor.execute(query+join_query+pagination_query, seller_list)

            seller_list_info = cursor.fetchall()

            cursor.execute(total_seller_count+join_query, seller_list)
            total_seller = cursor.fetchone()

            return seller_list_info, total_seller

    def get_seller_actions(self, db_connection):
        with db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT 
                ac.name as action_name,
                ac.id as action_id,
                ssa.before_status_id
            FROM 
                seller_statuses_actions AS ssa 
            JOIN 
                seller_statuses ON seller_statuses.id = ssa.before_status_id 
            JOIN 
                actions AS ac ON ac.id = ssa.action_id;
            """

            cursor.execute(query)
            results = cursor.fetchall()
            return results
