import config 

from flask import Flask
from flask_cors import CORS
# from flask.json import JSONEncoder

from controller.account_controller  import account_app
from controller.order_controller    import order_app
from controller.product_controller  import product_app
from controller.home_controller     import home_app

""" Flask 객체 
Returns: Flask 객체화를 통한 app 객체 생성 

Authors: 홍성은

History:
    2020-10-24 : 초기 생성
    2020-10-26 : 각 app에 url_prefix blueprint 등록 
"""
    
def create_app():
    app = Flask(__name__) # Flask를 객체화, 인스턴스를 app변수에 저장 
    app.debug = True
    app.config.from_pyfile('config.py') # config 설정
    CORS(app, resources={r'*' : {'origins':'*'}}) #CORS 설정
    
    app.register_blueprint(account_app, url_prefix='/account')
    app.register_blueprint(order_app,    url_prefix='/order')
    app.register_blueprint(product_app, url_prefix='/product')
    app.register_blueprint(home_app,    url_prefix='/home')

    return app