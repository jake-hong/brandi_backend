import jwt
import bcrypt
import datetime
from flask import request,jsonify
from config import SECRET, ALGORITHM
from model.account_dao import AccountDao
from model.product_dao import ProductDao
from model.order_dao import OrderDao

product_dao = ProductDao()
order_dao   = OrderDao()


from utils import error_code, get_filter, nav_to_dict

class AccountService():
    def signup(self, seller_info, db_connection):
        """회원가입된 새로운 셀러 생성 및 중복 확인 로직
        Args: 
            seller_info: controller에서 받은 셀러정보 변수
            db_connection: DB 커넥션 변수
        Returns: 
            데이터베이스 연결 오류, 200: {"message": "DATABASE_ERROR"}
            아이디 중복, 409: {"message": "DPLICATED_ID"} } 
            회원가입 성공, 200: {"message": "SUCCESS"} 
        Authors: 홍성은
        History:
            2020-10-26 : 초기 생성
            2020-10-27 : account_dao 연결 로직 수정
        """
        account_dao = AccountDao()
        try:
            # 데이터베이스 연결 여부 확인 
            if db_connection is None:
                return error_code({'error':'C0002'}), 500
            
            # account_dao 내부에서 중복인 id 확인
            account_id = account_dao.check_identification(seller_info['identification'], db_connection=db_connection)
            
            if account_id:
                return jsonify({'message':'DUPLICATED_ID'}), 409
            
            #셀러명 정보 넣기 
            korean_name = account_dao.check_korean_name(seller_info['korean_name'],db_connection=db_connection)
            # korean_name 중복일 경우 에러
            if korean_name: 
                return jsonify({'message': 'DUPLICATED_NAME'}),400     
            
            #영문 셀러명 정보 넣기 
            english_name = account_dao.check_english_name(seller_info['english_name'],db_connection=db_connection)
            # english_name 중복일 경우 에러
            if english_name: 
                return jsonify({'message': 'DUPLICATED_EN_NAME'}),400 
            
            #고객센터 번호 정보 넣기 
            cs_contact = account_dao.check_cs_contact(seller_info['cs_contact'],db_connection=db_connection)
            #고객센터 번호 중복일 경우 에러 
            if cs_contact: 
                return jsonify({'message': 'DUPLICATED_CS_CONTACT'}),400 

            # 중복 체크 통과시 bcrypt를 이용한 비밀번호 해싱
            bcrypt_password = seller_info['password'].encode('utf-8') 
            seller_info['password'] = bcrypt.hashpw(bcrypt_password,bcrypt.gensalt()).decode('utf-8')

            #account_dao 내부에서 회원가입 진행한 결과 값 리턴
            result = account_dao.signup_account(seller_info, db_connection=db_connection)
            return result
                
        except Exception:
            return jsonify({'error':'C0002'})

    def get_seller_list(self, seller_list, db_connection):
        """셀러 리스트 보내주기 
        Args: 
            seller_list : 셀러정보
            db_connection : DB 커넥션 

        Returns: 
            셀러 리스트 
        Authors: 
            홍성은
        History:
            2020-10-27 : 셀러리스트 초기 생성
            2020-10-29 : 유효성 검사 추가 
            2020-10-31 : 셀러 검색 기능 추가
            2020-11-05 : 셀러 액션변경 기능 추가 
        """
        account_dao = AccountDao()
        if seller_list is None:
            return errorcode ({'error':'INVALID_ARGUMENTS'})
        
        seller_list_info,total_seller = account_dao.get_seller_list(seller_list,db_connection=db_connection)
        
        #입점 상태에 따른 actions 상태 받기
        action_list = account_dao.get_seller_actions(db_connection=db_connection)
        
        # 입점 상태(before_staus_id)에 맞추어 action id 값과 action_name 값을 가져옴. 
        actions = {
            1 : [],
            2 : [],
            3 : [],
            4 : [],
            }
        for i in range(1,8):
            for action in action_list:
                if action['before_status_id'] == i:
                    actions[i].append({
                        'action_id': action['action_id'],
                        'action_name': action['action_name']
                    })    

        for seller in seller_list_info:
            seller['actions'] = actions[seller['status_id']]
            print()
        return {'success':{'data':seller_list_info ,'total_seller_number':[total_seller]}}

    def signin(self, data, db_connection):
        """
        로그인 API [GET]
        
        Args:
            account_id  : 유저 id
            password    : 비밀번호
        Returns:
            Success     : {access_token : token}, 200
            key error   : {message : KEY_ERROR}, code : 400
            로그인 ID 오류   : {message : USER_DOES_NOT_EXIST}, code : 400
            비밀번호 불일치   : {message' : INVALID ACCESS}
        
        Authors: 김수정
        History:
        2020-10-27 : 초기 생성
        """

        try:
            account_dao = AccountDao()
            data['password'] = data['password'].encode('utf-8') # data 가 딕셔너리가 아니면 타입에러 남
            account = account_dao.login_account(db_connection, {'identification':data['identification']}) 

            # 등록된 사용자의 경우
            if account:

                # 입점 대기중인 셀러인지 확인 (셀러이고 입점 대기중이면 True)
                is_seller_not_validated = account_dao.is_seller_not_validated(db_connection, {'account_id':account['id']})
                 
                # 입점 대기중인 경우
                if is_seller_not_validated:
                    return {'error':"A1014"}
                 
                # 셀러가 아니거나 입점 대기중이 아니면, 
                # 비밀번호 확인
                if not bcrypt.checkpw(
                    data['password'], account['password'].encode('utf-8')
                    ):            

                    # 비밀번호 틀림
                    return {'error':"A1012"}
                # 비밀번호 맞음
                account_id = account['id']
                access_token = jwt.encode({'account_id': account_id}, SECRET, ALGORITHM)
                
                # 마스터인지 확인
                master_check = account_dao.check_master(db_connection, {'account_id':account_id})
                # 마스터/ 셀러 여부에 맞는 필터 불러옴
                if master_check:
                    is_master = True
                else:
                    is_master = False
               
                filter_list = get_filter(db_connection, is_master)
                nav_rows    = account_dao.get_navs(db_connection, is_master)
                print(nav_rows)
                nav_list    = nav_to_dict(nav_rows)

                print(nav_list) 
                return {
                    'success': {
                        'Authorization' : access_token.decode('utf-8'), 
                        'is_master'     : is_master, 
                        'filter_list'   : filter_list, 
                        'nav_list'      : nav_list
                        }
                    }
                
            # 미동록 사용자
            return {'error':"A1011"}
        
        except Exception as error:
            return {'error':"C0001", 'programming_error':error}

    def get_seller_info(self, seller_id, db_connection, request):
        """
        셀러 정보 수정 페이지에서 기존 데이터를 호출 API [GET]
        작성자: 김수정
        Args:
            seller_id  : 해당 셀러의 정보를 가져옴
        Returns:
        
        Authors: 김수정
        History:
            2020-10-27 : 초기 생성
        """
        account_dao = AccountDao()
        account_id = request.account_id

        is_master = account_dao.check_master(db_connection, {'account_id':account_id})

        try:

            # 셀러인 경우 - 셀러 상태 변경자 이름 삭제
            if not is_master:
                result_general   = account_dao.get_general_info(db_connection, {'seller_id':seller_id}) # 일반 정보 담아옴
                result_log       = account_dao.get_status_log(db_connection, {'seller_id':seller_id}) # 셀러 상태 변경기록 담아옴
                result_manager   = account_dao.get_manager_info(db_connection, {'seller_id':seller_id}) # 셀러의 담당자 정보 담아옴

                # result_log 에서 속성 변경해준 담당자 이름 삭제
                if result_log['seller_status_log']:
                    for log in result_log['seller_status_log']:
                        del log['updated_by']
                
                # 하나의 딕셔너리에 다 담아줌
                result_general.update(result_log)
                result_general.update(result_manager)

            else:
                # 마스터인 경우 - 셀러의 속성(ex. 마켓) 외에 다른 속성들의 리스트와 id 를 함께 전송하여 수정 가능하도록 함
                result_general   = account_dao.get_general_info(db_connection, {'seller_id':seller_id}) # 일반 정보 담아옴
                result_log       = account_dao.get_status_log(db_connection, {'seller_id':seller_id}) # 셀러 상태 변경기록 담아옴
                result_manager   = account_dao.get_manager_info(db_connection, {'seller_id':seller_id}) # 셀러의 담당자 정보 담아옴
                result_attribute = account_dao.get_attributes(db_connection)

                # result_attribute (모든 속성 이름) 과 result_general 의 attribute (해당 셀러의 속성)을 비교하여 result_general 에 'attributes' 에 담아줌  
                for i in result_attribute['attributes']:
                    i['check'] = True if i['category_title'] == result_general['attribute'] else False

                del result_general['attribute']

                result_general.update(result_attribute)
                result_general.update(result_log)
                result_general.update(result_manager)

            return {'success' : result_general}

        except Exception as exception:
            return error_code({'error':'A1031', 'programming_error':exception})    
    
    def change_seller_status(self, db_connection, body):
        """
        셀러 입점상태 변경 [POST]]
        Args:
            db_connection : db
            body : request.json
                seller_id : seller 의 account_id
                action_id : 선택한 action 의 id 
        Returns:
            Success     : {'success': {내용}}, 200
        
        Authors: 김수정
        History:
        2020-10-29 : 초기 생성
        """
        account_dao = AccountDao()

        try:
            # 셀러의 현재 상태 확인
            result = account_dao.action_check(db_connection, body)

            data = {
                'seller_id' : body['seller_id'], 
                'master_id' : request.account_id, 
                'after_status_id' : result['after_status_id']
            }

            # 셀러의 상태와 요청받은 액션 정보가 일치하는 경우
            if result:
                master_id = request.account_id
                result = account_dao.action_change(db_connection, data)
                if result:
                    return {'success':'updated'}

            # 액션번호와 셀러상태가 불일치
            return {'error':"A1051"}
        
        # 기타 에러
        except Exception as error:
            return {'error':"C0001", 'programming_error':error} 

    def get_home_info(self, db_connection):
        """
        셀러 로그인시 매출 통계자료를 불러오는 함수입니다. 
        Args:
            db_connection : db
        Returns:
            Success     : {'success': 
                { 'products_on_sale' : 판매중인 상품 수,
                  'total_product'    : 전체 상품 수,
                  'statistics'       : {'datetime':날짜, 'sales':일 매출액, 'count':일 판매건수} * 30개
                }
            }, 200
        Authors: 김수정
        History:
        2020-11-01 : 초기 생성
        """
        account_dao = AccountDao()
        product_dao = ProductDao()
        order_dao   = OrderDao()

        account_id = request.account_id

        try:
            # 전체 상품을 가져옴
            product_result = product_dao.get_all_product_for_seller(db_connection, {'account_id':account_id})
            # 전체 상품 갯수
            number_of_all_products = len(product_result)
            
            # 판매중, 진열중, 미삭제된 상품의 갯수
            number_of_available_products = 0
            for product in product_result:      
                if (
                    product['is_displayed'] and
                    product['is_on_sale'] and
                    not product['is_deleted']
                ):
                    number_of_available_products += 1
            
            # 지난 한달간의 주문을 다 가져옴
            now = datetime.datetime.now()
            today = datetime.datetime(now.year, now.month, now.day)
            last_month = today - datetime.timedelta(29, 0)

            order_result = order_dao.get_one_month_orders(
                    db_connection, {
                        'account_id' : account_id,
                        'last_month' : last_month,
                    }
            )

            # 일자별로 분류해서 매출 건수와 매출액을 0으로 우선 입력해둠
            order_dict_list = [
            { 
                'datetime' : str(
                    (last_month + datetime.timedelta(i, 0)).month)\
                    +\
                    '/'\
                    +str((last_month+datetime.timedelta(i, 0)).day),
                'count' : 0,
                'sales' : 0
            } for i in range(30)]

            order_preparing = 0
            order_delivered = 0

            # 결제 한 건당 
            for order in order_result:
                order_date = order['ordered_at']    
                order_midnight = datetime.datetime(order_date.year, order_date.month, order_date.day)

                # 주문 날짜로 order_dict_list 의 index 를 구함
                index = (now-order_midnight).days

                # 매출 건수를 1 더해줌
                order_dict_list[29-index]['count'] += 1
                
                # 매출액을 더해줌
                price = order['price']*order['discount_rate']*order['quantity']
                order_dict_list[29-index]['sales'] += price

                if order['status_name'] == "상품준비":
                    order_preparing += 1

                if order['status_name'] == "배송완료":
                    order_delivered += 1

            return {'success':
                {
                'total_product'    : number_of_all_products,
                'products_on_sale' : number_of_available_products,
                'statistics'       : order_dict_list,
                'order_preparing'  : order_preparing,
                'order_delivered'  : order_delivered 
                }
            }   

        # 기타 에러
        except Exception as error:
            return {'error':"C0001", 'programming_error':error}