DROP DATABASE IF EXISTS brandi;
CREATE DATABASE IF NOT EXISTS brandi character set utf8mb4 collate utf8mb4_general_ci;
USE brandi;

-- account_types Table Create SQL
CREATE TABLE account_types
(
    id    INT            NOT NULL    AUTO_INCREMENT, 
    name  VARCHAR(45)    NOT NULL    UNIQUE COMMENT '(master, seller)', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '계정 유형(master,sellr)';

-- account_types Table Create SQL
CREATE TABLE accounts
(
    id               INT            NOT NULL    AUTO_INCREMENT, 
    identification   VARCHAR(45)    NOT NULL     UNIQUE COMMENT '계정 아이디',
    password         VARCHAR(500)   NOT NULL            COMMENT '비밀번호', 
    account_type_id  INT            NOT NULL  DEFAULT 2 COMMENT '(master,seller)',  
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '계정';

ALTER TABLE accounts
    ADD CONSTRAINT FK_accounts_account_type_id_account_types_id FOREIGN KEY (account_type_id)
        REFERENCES account_types (id) ON DELETE CASCADE;

-- account_types Table Create SQL
CREATE TABLE seller_statuses
(
    id    INT            NOT NULL    AUTO_INCREMENT, 
    name  VARCHAR(45)    NOT NULL    COMMENT '셀러상태(입점,휴업,폐업)', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '셀러상태';

-- account_types Table Create SQL
CREATE TABLE seller_attributes
(
    id    INT            NOT NULL    AUTO_INCREMENT, 
    name  VARCHAR(45)    NULL        COMMENT '셀태속성(쇼핑몰,마켓,로드샵)', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '셀러속성';

-- account_types Table Create SQL
CREATE TABLE sellers
(
    id                             INT            NOT NULL    AUTO_INCREMENT, 
    account_id                     INT            NOT NULL    COMMENT '셀러의 account_id',
    contact                        VARCHAR(45)    NOT NULL    COMMENT '전화번호',  
    attribute_id                   INT            NOT NULL    COMMENT '셀러속성',
    korean_name                    VARCHAR(45)    NOT NULL    UNIQUE COMMENT '한국명',   
    english_name                   VARCHAR(45)    NOT NULL    UNIQUE COMMENT '영문명', 
    created_at                     DATETIME       NOT NULL    DEFAULT CURRENT_TIMESTAMP COMMENT '최초 생성일',
    status_id                      INT            NOT NULL    COMMENT '셀러상태', 
    email                          VARCHAR(45)    NULL        COMMENT '이메일', 
    thumbnail_url                  VARCHAR(1000)  NULL        COMMENT '셀러 프로필', 
    background_image_url           VARCHAR(1000)  NULL        COMMENT '셀러페이지 배경이미지', 
    introduction                   VARCHAR(500)   NULL        COMMENT '셀러 한줄 소개', 
    description                    LONGTEXT       NULL        COMMENT '셀러 상세 소개', 
    zip_code                       VARCHAR(45)    NULL        COMMENT '우편번호', 
    address                        VARCHAR(45)    NULL        COMMENT '도로명주소', 
    detail_address                 VARCHAR(45)    NULL        COMMENT '상세주소', 
    is_deleted                     TINYINT(1)     NOT NULL    DEFAULT 0 COMMENT '소프트델리트', 
    cs_contact                     VARCHAR(45)    NULL        COMMENT '고객센터번호', 
    cs_from                        TIME           NULL        COMMENT '고객센터시작시간', 
    cs_until                       TIME           NULL        COMMENT '마감시간', 
    cs_weekend_from                TIME           NULL        COMMENT '고객센터시작시간(주말)', 
    cs_weekend_until               TIME           NULL        COMMENT '고객센터마감시간(주말)', 
    updated_at                     DATETIME       NOT NULL    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  
    updater_id                     INT            NULL        COMMENT '수정한 사람', 
    refund_info                    VARCHAR(1000)   NULL        COMMENT '교환/환불정보',
    shipment_info                  VARCHAR(1000)   NULL        COMMENT '배송정보',
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '셀러정보';

ALTER TABLE sellers
    ADD CONSTRAINT FK_sellers_status_id_seller_statuses_id FOREIGN KEY (status_id)
        REFERENCES seller_statuses (id) ON DELETE CASCADE;

ALTER TABLE sellers
    ADD CONSTRAINT FK_sellers_attribute_id_seller_attributes_id FOREIGN KEY (attribute_id)
        REFERENCES seller_attributes (id) ON DELETE CASCADE;

ALTER TABLE sellers
    ADD CONSTRAINT FK_sellers_account_id_accounts_id FOREIGN KEY (account_id)
        REFERENCES accounts (id) ON DELETE CASCADE;

ALTER TABLE sellers
    ADD CONSTRAINT FK_sellers_updater_id_accounts_id FOREIGN KEY (updater_id)
        REFERENCES accounts (id) ON DELETE CASCADE;


-- account_types Table Create SQL
CREATE TABLE cates
(
    id        INT            NOT NULL    AUTO_INCREMENT, 
    name      VARCHAR(45)    NOT NULL UNIQUE COMMENT '(아우터/치마)', 
    ordering  INT            NOT NULL UNIQUE COMMENT '(1~4)', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '카테고리';;


-- account_types Table Create SQL
CREATE TABLE sub_cates
(
    id        INT            NOT NULL    AUTO_INCREMENT, 
    name      VARCHAR(45)    NOT NULL UNIQUE COMMENT '(자켓/가디건 등)', 
    ordering  INT            NOT NULL UNIQUE COMMENT '(1~22)', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '서브카테고리';


-- account_types Table Create SQL
CREATE TABLE cate_sets
(
    id               INT    NOT NULL    AUTO_INCREMENT, 
    cate_id      INT    NOT NULL COMMENT '(아우터/치마)', 
    sub_cate_id  INT    NOT NULL COMMENT '(자켓/가디건 등)', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '카테고리셋';

ALTER TABLE cate_sets
    ADD CONSTRAINT FK_cates_sets_cate_id_cates_id FOREIGN KEY (cate_id)
        REFERENCES cates (id) ON DELETE CASCADE;

ALTER TABLE cate_sets
    ADD CONSTRAINT FK_cates_sets_sub_cate_id_sub_cates_id FOREIGN KEY (sub_cate_id)
        REFERENCES sub_cates (id) ON DELETE CASCADE;


-- account_types Table Create SQL
CREATE TABLE countries_of_origin
(
    id    INT            NOT NULL    AUTO_INCREMENT, 
    name  VARCHAR(45)    NOT NULL    UNIQUE  COMMENT '한국/중국', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '제조국';


-- account_types Table Create SQL
CREATE TABLE products
(
    id                         INT             NOT NULL    AUTO_INCREMENT, 
    name                       VARCHAR(100)    NOT NULL COMMENT '상품명', 
    seller_id                  INT             NOT NULL COMMENT '셀러번호', 
    cate_set_id     INT        NOT NULL        COMMENT '상품의 카테고리/섭카테고리', 
    introduction               VARCHAR(150)    NULL     COMMENT '한줄소개', 
    description                LONGTEXT        NOT NULL COMMENT '상품소개', 
    price                      INT             NOT NULL COMMENT '가격', 
    max_quantity               INT             NOT NULL COMMENT '최소 구매가능수량', 
    min_quantity               INT             NOT NULL COMMENT '최대 구매가능수량', 
    discount_rate              INT             NULL     COMMENT '할인률', 
    discount_validate_from     DATETIME        NULL     COMMENT '할인시작일', 
    discount_validate_until    DATETIME        NULL     COMMENT '할인종료일', 
    manufacturer               VARCHAR(45)     NULL     COMMENT '제조사', 
    manufactured_at            DATE            NULL     COMMENT '제조일자', 
    country_of_origin_id       INT             NULL     COMMENT '제조국', 
    is_displayed               TINYINT(1)      DEFAULT 1   NOT NULL COMMENT '진열여부', 
    is_on_sale                 TINYINT(1)      DEFAULT 1   NOT NULL COMMENT '판매여부', 
    created_at                 DATETIME        NOT NULL    DEFAULT CURRENT_TIMESTAMP COMMENT '등록일', 
    updated_at                 DATETIME        NULL        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '최종 수정일', 
    updater_id                 INT             NOT NULL    COMMENT '최종수정인',    
    is_deleted                 TINYINT(1)      DEFAULT 0   NOT NULL COMMENT '삭제여부(soft_delete)', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '상품정보';

ALTER TABLE products
    ADD CONSTRAINT FK_products_country_of_origin_id_countries_of_origin_id FOREIGN KEY (country_of_origin_id)
        REFERENCES countries_of_origin (id) ON DELETE CASCADE;

ALTER TABLE products
    ADD CONSTRAINT FK_products_updater_id_accounts_id FOREIGN KEY (updater_id)
        REFERENCES accounts (id) ON DELETE CASCADE;

ALTER TABLE products
    ADD CONSTRAINT FK_products_cate_set_id_cate_sets_id FOREIGN KEY (cate_set_id)
        REFERENCES cate_sets (id) ON DELETE CASCADE;

ALTER TABLE products MODIFY description longtext NULL;  

-- account_types Table Create SQL
CREATE TABLE receivers
(
    id              INT            NOT NULL    AUTO_INCREMENT, 
    name            VARCHAR(45)    NOT NULL    COMMENT '주문자명', 
    contact         VARCHAR(45)    NOT NULL    COMMENT '전화번호', 
    zip_code        VARCHAR(45)    NOT NULL    COMMENT '우편번호', 
    street_address  VARCHAR(100)   NOT NULL    COMMENT '도로명주소', 
    detail_address  VARCHAR(100)   NOT NULL    COMMENT '상세주소', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '수령보정보';


-- account_types Table Create SQL
CREATE TABLE detail_order_statuses
(
    id    INT            NOT NULL    AUTO_INCREMENT, 
    name  VARCHAR(45)    NOT NULL    UNIQUE COMMENT '주문상태', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '주문상태';

ALTER TABLE detail_order_statuses COMMENT '주문상태';


CREATE TABLE order_actions
(
    id    INT            NOT NULL    AUTO_INCREMENT PRIMARY KEY, 
    before_id     INT NOT NULL COMMENT '전 상태',
    after_id      INT NOT NULL COMMENT '이후 상태'
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

ALTER TABLE detail_order_statuses COMMENT '주문상태변경';


ALTER TABLE order_actions
    ADD CONSTRAINT FK_order_actions_before_id_detail_order_statuses_id FOREIGN KEY (before_id)
        REFERENCES detail_order_statuses (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE order_actions
    ADD CONSTRAINT FK_order_actions_after_id_detail_order_statuses_id FOREIGN KEY (after_id)
        REFERENCES detail_order_statuses (id) ON DELETE RESTRICT ON UPDATE RESTRICT;



-- account_types Table Create SQL
CREATE TABLE sizes
(
    id    INT            NOT NULL    AUTO_INCREMENT, 
    name  VARCHAR(45)    NOT NULL    UNIQUE COMMENT '250/large', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '옵션_사이즈';

-- account_types Table Create SQL
CREATE TABLE colors
(
    id    INT            NOT NULL    AUTO_INCREMENT, 
    name  VARCHAR(45)    NOT NULL    UNIQUE COMMENT '빨강/파랑', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '옵션_컬러';

-- account_types Table Create SQL
CREATE TABLE orders
(
    id                 INT               NOT NULL    AUTO_INCREMENT, 
    paied_at           DATETIME          NOT NULL    DEFAULT CURRENT_TIMESTAMP  COMMENT '결제일자', 
    total_paied_price  DECIMAL(18, 4)    NOT NULL    COMMENT '결제금액', 
    receiver_id        INT               NOT NULL    COMMENT '수령인/배송지 정보', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '결제정보';

ALTER TABLE orders
    ADD CONSTRAINT FK_orders_receiver_id_receivers_id FOREIGN KEY (receiver_id)
        REFERENCES receivers (id) ON DELETE CASCADE;


-- account_types Table Create SQL
CREATE TABLE options
(
    id                   INT         NOT NULL    AUTO_INCREMENT, 
    product_id           INT         NOT NULL    COMMENT '상품번호 FK', 
    size_id              INT         NOT NULL    COMMENT '사이즈', 
    color_id             INT         NOT NULL    COMMENT '색상', 
    is_stock_controlled  TINYINT(1)  NOT NULL    COMMENT '재고관리여부', 
    stock_quantity       INT         NULL        COMMENT '재고수량', 
    is_deleted           TINYINT(1)  NOT NULL    DEFAULT 0  COMMENT'삭제여부', 
    updater_id           INT         NOT NULL    COMMENT'수정자',
    updated_at           DATETIME    NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT '수정일',
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '옵션';

ALTER TABLE options
    ADD CONSTRAINT FK_options_size_id_sizes_id FOREIGN KEY (size_id)
        REFERENCES sizes (id) ON DELETE CASCADE;

ALTER TABLE options
    ADD CONSTRAINT FK_options_color_id_colors_id FOREIGN KEY (color_id)
        REFERENCES colors (id) ON DELETE CASCADE;

ALTER TABLE options
    ADD CONSTRAINT FK_options_product_id_products_id FOREIGN KEY (product_id)
        REFERENCES products (id) ON DELETE CASCADE;

ALTER TABLE options
    ADD CONSTRAINT FK_options_updater_id_sellers_id FOREIGN KEY (updater_id)
        REFERENCES sellers (id) ON DELETE CASCADE;

-- account_types Table Create SQL
CREATE TABLE menus
(
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(45) NOT NULL UNIQUE COMMENT '네비게이션바',
    PRIMARY KEY(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT'메뉴';

-- account_types Table Create SQL
CREATE TABLE sub_menus
(
    id    INT            NOT NULL AUTO_INCREMENT, 
    name  VARCHAR(45)    NOT NULL UNIQUE COMMENT '하위 메뉴', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '하위메뉴';


-- account_types Table Create SQL
CREATE TABLE actions
(
    id    INT           NOT NULL AUTO_INCREMENT, 
    name  VARCHAR(45)   NOT NULL UNIQUE    COMMENT'actions', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT 'actions(휴점신청,폐점신청)';


-- account_types Table Create SQL
CREATE TABLE detail_orders
(
    id             INT         NOT NULL    AUTO_INCREMENT, 
    order_id       INT         NOT NULL    COMMENT '큰 주문', 
    product_id     INT         NOT NULL    COMMENT '상품명', 
    seller_id      INT         NOT NULL    COMMENT '셀러정보', 
    receiver_id    INT         NOT NULL    COMMENT '수령인/배송지 정보', 
    option_id      INT         NOT NULL    COMMENT '옵션정보', 
    status_id      INT         NOT NULL    COMMENT '주문상태', 
    price          INT         NOT NULL    COMMENT '가격', 
    discount_rate  INT         NOT NULL    COMMENT '할인율', 
    quantity       INT         NOT NULL    COMMENT '수량', 
    ordered_at     DATETIME    NOT NULL    DEFAULT CURRENT_TIMESTAMP COMMENT '주문시점', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '세부주문내역';

ALTER TABLE detail_orders
    ADD CONSTRAINT FK_detail_orders_status_id_detail_order_statuses_id FOREIGN KEY (status_id)
        REFERENCES detail_order_statuses (id) ON DELETE CASCADE;

ALTER TABLE detail_orders
    ADD CONSTRAINT FK_detail_orders_receiver_id_receivers_id FOREIGN KEY (receiver_id)
        REFERENCES receivers (id) ON DELETE CASCADE;

ALTER TABLE detail_orders
    ADD CONSTRAINT FK_detail_orders_option_id_options_id FOREIGN KEY (option_id)
        REFERENCES options (id) ON DELETE CASCADE;

ALTER TABLE detail_orders
    ADD CONSTRAINT FK_detail_orders_order_id_orders_id FOREIGN KEY (order_id)
        REFERENCES orders (id) ON DELETE CASCADE;

ALTER TABLE detail_orders
    ADD CONSTRAINT FK_detail_orders_product_id_products_id FOREIGN KEY (product_id)
        REFERENCES products (id) ON DELETE CASCADE;

ALTER TABLE detail_orders
    ADD CONSTRAINT FK_detail_orders_seller_id_sellers_id FOREIGN KEY (seller_id)
        REFERENCES sellers (id) ON DELETE CASCADE;


-- account_types Table Create SQL
CREATE TABLE menu_sets
(
    id           INT    NOT NULL    AUTO_INCREMENT, 
    menu_id      INT    NOT NULL    COMMENT '네비게이션바', 
    sub_menu_id  INT    NOT NULL    COMMENT '누르면 나오는것', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '메뉴셋';

ALTER TABLE menu_sets
    ADD CONSTRAINT FK_menu_sets_menu_id_menus_id FOREIGN KEY (menu_id)
        REFERENCES menus (id) ON DELETE CASCADE;

ALTER TABLE menu_sets
    ADD CONSTRAINT FK_menu_set_sub_menu_id_sub_menus_id FOREIGN KEY (sub_menu_id)
        REFERENCES sub_menus (id) ON DELETE CASCADE;


-- account_types Table Create SQL
CREATE TABLE seller_statuses_actions
(
    id               INT    NOT NULL    AUTO_INCREMENT, 
    before_status_id INT    NOT NULL    COMMENT '변경 전 셀러 상태', 
    action_id        INT    NOT NULL    COMMENT 'actions',
    after_status_id  INT    NOT NULL    COMMENT '변경 후 셀러 상태',
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '셀러상태';

ALTER TABLE seller_statuses_actions
    ADD CONSTRAINT FK_seller_statuses_actions_before_status_id_seller_statuses_id FOREIGN KEY (before_status_id)
        REFERENCES seller_statuses (id) ON DELETE CASCADE;

ALTER TABLE seller_statuses_actions
    ADD CONSTRAINT FK_seller_statuses_actions_action_id_actions_id FOREIGN KEY (action_id)
        REFERENCES actions (id) ON DELETE CASCADE;

ALTER TABLE seller_statuses_actions
    ADD CONSTRAINT FK_seller_statuses_actions_after_status_id_seller_statuses_id FOREIGN KEY (after_status_id)
        REFERENCES seller_statuses (id) ON DELETE CASCADE;

-- account_types Table Create SQL
CREATE TABLE managers
(
    id          INT            NOT NULL    AUTO_INCREMENT, 
    seller_id   INT            NOT NULL    COMMENT '셀러 번호', 
    name        VARCHAR(45)    NOT NULL    COMMENT '담당자 이름', 
    contact     VARCHAR(45)    NOT NULL    COMMENT '담당자 연락처', 
    email       VARCHAR(45)    NOT NULL    COMMENT '담당자 이메일', 
    ordering    INT            NOT NULL    COMMENT '담당자 순서(1,2,3)', 
    updated_at  DATETIME       NOT NULL    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일', 
    updater_id  INT            NOT NULL    COMMENT '최종 수정자', 
    is_deleted  TINYINT(1)     NOT NULL    DEFAULT 0 COMMENT '삭제여부', 
    deleter_id  INT            NULL     COMMENT '삭제자', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '담당자정보';

ALTER TABLE managers
    ADD CONSTRAINT FK_managers_seller_id_sellers_id FOREIGN KEY (seller_id)
        REFERENCES sellers (id) ON DELETE CASCADE;

ALTER TABLE managers
    ADD CONSTRAINT FK_managers_deleter_id_accounts_id FOREIGN KEY (deleter_id)
        REFERENCES accounts (id) ON DELETE CASCADE;

ALTER TABLE managers
    ADD CONSTRAINT FK_managers_updater_id_accounts_id FOREIGN KEY (updater_id)
        REFERENCES accounts (id) ON DELETE CASCADE;


-- account_types Table Create SQL
CREATE TABLE seller_status_log
(
    id                 INT         NOT NULL    AUTO_INCREMENT, 
    changed_at         DATETIME    NOT NULL    DEFAULT CURRENT_TIMESTAMP COMMENT '셀러상태 변경 기록', 
    seller_id          INT         NOT NULL    COMMENT '셀러', 
    changed_status_id  INT         NOT NULL    COMMENT '변경된 상태', 
    updater_id         INT         NOT NULL    COMMENT '수정자',
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '셀러상태기록';

ALTER TABLE seller_status_log
    ADD CONSTRAINT FK_seller_status_log_changed_status_id_seller_statuses_id FOREIGN KEY (changed_status_id)
        REFERENCES seller_statuses (id) ON DELETE CASCADE;

ALTER TABLE seller_status_log
    ADD CONSTRAINT FK_seller_status_log_seller_id_sellers_id FOREIGN KEY (seller_id)
        REFERENCES sellers (id) ON DELETE CASCADE;

ALTER TABLE seller_status_log
    ADD CONSTRAINT FK_seller_status_log_updater_id_sellers_id FOREIGN KEY (updater_id)
        REFERENCES sellers (id) ON DELETE CASCADE;


-- account_types Table Create SQL
CREATE TABLE product_images
(
    id          INT              NOT NULL    AUTO_INCREMENT, 
    product_id  INT              NOT NULL    COMMENT '상품', 
    image_url   VARCHAR(1000)    NOT NULL    COMMENT '이미지URL', 
    ordering    INT              NOT NULL    COMMENT '순서(1~5)', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '상품이미지';

ALTER TABLE product_images
    ADD CONSTRAINT FK_product_images_product_id_products_id FOREIGN KEY (product_id)
        REFERENCES products (id) ON DELETE CASCADE;


-- account_types Table Create SQL
CREATE TABLE product_log
(
    id              INT         NOT NULL    AUTO_INCREMENT, 
    product_id      INT         NOT NULL    COMMENT '상품', 
    validate_from   DATETIME    NOT NULL    DEFAULT CURRENT_TIMESTAMP COMMENT '시작일', 
    validate_until  DATETIME    NOT NULL    COMMENT '종료일', 
    price           INT         NOT NULL    COMMENT '가격', 
    discount_rate   INT         NOT NULL    COMMENT '할인율', 
    discount_from   DATETIME    NOT NULL    COMMENT '할인시작일', 
    discount_until  DATETIME    NOT NULL    COMMENT '할인종료일', 
    updater_id      INT         NOT NULL    COMMENT '수정자', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '가격기록';

ALTER TABLE product_log
    ADD CONSTRAINT FK_product_log_product_id_products_id FOREIGN KEY (product_id)
        REFERENCES products (id) ON DELETE CASCADE;

ALTER TABLE product_log
    ADD CONSTRAINT FK_product_log_updater_id_accounts_id FOREIGN KEY (updater_id)
        REFERENCES accounts (id) ON DELETE CASCADE;


-- account_types Table Create SQL
CREATE TABLE detail_order_status_log
(
    id               INT         NOT NULL    AUTO_INCREMENT, 
    status_id        INT         NOT NULL    COMMENT '주문상태', 
    detail_order_id  INT         NOT NULL    COMMENT '상세주문', 
    changed_at       DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '날짜', 
    updater_id       INT         NOT NULL    COMMENT '수정자', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '세부주문 상태 ';

ALTER TABLE detail_order_status_log COMMENT '주문상태기록';

ALTER TABLE detail_order_status_log
    ADD CONSTRAINT FK_detail_order_status_log_detail_order_id_detail_orders_id FOREIGN KEY (detail_order_id)
        REFERENCES detail_orders (id) ON DELETE CASCADE;

ALTER TABLE detail_order_status_log
    ADD CONSTRAINT FK_detail_order_status_log_status_id_detail_order_statuses_id FOREIGN KEY (status_id)
        REFERENCES detail_order_statuses (id) ON DELETE CASCADE;

ALTER TABLE detail_order_status_log
    ADD CONSTRAINT FK_detail_order_status_log_updater_id_accounts_id FOREIGN KEY (updater_id)
        REFERENCES accounts (id) ON DELETE CASCADE;


-- account_types Table Create SQL
CREATE TABLE masters
(
    id           INT            NOT NULL    AUTO_INCREMENT, 
    account_id  INT            NOT NULL     COMMENT '계정', 
    name        VARCHAR(45)    NOT NULL     COMMENT '이름', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '마스터 계정';

ALTER TABLE masters
    ADD CONSTRAINT FK_masters_account_id_accounts_id FOREIGN KEY (account_id)
        REFERENCES accounts (id) ON DELETE CASCADE;


-- account_types Table Create SQL
CREATE TABLE menu_sets_account_types
(
    id               INT    NOT NULL  AUTO_INCREMENT, 
    menu_set_id      INT    NOT NULL  COMMENT '네비게이션바', 
    account_type_id  INT    NOT NULL  COMMENT '셀러/마스터인지', 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT '메뉴세트와 계정유형';

ALTER TABLE menu_sets_account_types
    ADD CONSTRAINT FK_menu_sets_account_types_menu_set_id_menu_sets_id FOREIGN KEY (menu_set_id)
        REFERENCES menu_sets(id) ON DELETE CASCADE;

ALTER TABLE menu_sets_account_types
    ADD CONSTRAINT FK_menu_sets_account_types_account_type_id_account_types_id FOREIGN KEY (account_type_id)
        REFERENCES account_types (id) ON DELETE CASCADE;