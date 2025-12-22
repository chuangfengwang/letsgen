CREATE DATABASE letsgen_db
    WITH ENCODING 'UTF8'
    LC_COLLATE = 'C.UTF-8'
    LC_CTYPE = 'C.UTF-8'
;
ALTER DATABASE letsgen_db SET timezone = 'Asia/Shanghai';

-- 用户表
create table letsgen_user
(
    id            BIGSERIAL          not null,
    user_name     varchar(50) UNIQUE not null default '',
    user_email    varchar(100)       not null default '',
    user_password varchar(100)       not null default '',
    user_phone    varchar(20)        not null default '',
    ui_role       varchar(10)        not null default '',
    user_status   varchar(10)        not null default '',
    note          text               not null default '',
    create_at     TIMESTAMPTZ        not null default now(),
    update_at     TIMESTAMPTZ        not null default now(),
    PRIMARY KEY (id)
);
CREATE INDEX idx_letsgen_user_email ON letsgen_user (user_email);
CREATE INDEX idx_letsgen_user_phone ON letsgen_user (user_phone);
CREATE INDEX idx_letsgen_user_create_at ON letsgen_user (create_at);
CREATE INDEX idx_letsgen_user_update_at ON letsgen_user (update_at);

COMMENT ON TABLE letsgen_user IS 'UI登录用户表';
COMMENT ON COLUMN letsgen_user.id IS '主键';
COMMENT ON COLUMN letsgen_user.user_name IS '用户名';
COMMENT ON COLUMN letsgen_user.user_email IS '用户邮箱';
COMMENT ON COLUMN letsgen_user.user_password IS '用户密码';
COMMENT ON COLUMN letsgen_user.user_phone IS '用户手机号';
COMMENT ON COLUMN letsgen_user.ui_role IS 'UI角色:admin,normal';
COMMENT ON COLUMN letsgen_user.user_status IS '用户状态:ok,disabled,pending';
COMMENT ON COLUMN letsgen_user.note IS '账号备注';
COMMENT ON COLUMN letsgen_user.create_at IS '创建时间';
COMMENT ON COLUMN letsgen_user.update_at IS '更新时间';

-- 计费账号表
create table letsgen_bill_account
(
    id               BIGSERIAL          not null,
    account_name     varchar(50) UNIQUE not null default '',
    account_status   varchar(10)        not null default '',
    create_user_name varchar(50)        not null default '',
    note             text               not null default '',
    create_at        TIMESTAMPTZ        not null default now(),
    update_at        TIMESTAMPTZ        not null default now(),
    PRIMARY KEY (id)
);
CREATE INDEX idx_letsgen_bill_account_create_at ON letsgen_bill_account (create_at);
CREATE INDEX idx_letsgen_bill_account_update_at ON letsgen_bill_account (update_at);

COMMENT ON TABLE letsgen_bill_account IS '计费账号表';
COMMENT ON COLUMN letsgen_bill_account.id IS '主键';
COMMENT ON COLUMN letsgen_bill_account.account_name IS '计费账号名';
COMMENT ON COLUMN letsgen_bill_account.account_status IS '计费账号状态:ok,disabled';
COMMENT ON COLUMN letsgen_bill_account.create_user_name IS '创建者用户名';
COMMENT ON COLUMN letsgen_bill_account.note IS '账号备注';
COMMENT ON COLUMN letsgen_bill_account.create_at IS '创建时间';
COMMENT ON COLUMN letsgen_bill_account.update_at IS '更新时间';

-- 用户-账户关系表 letsgen_user_account_rlt
create table letsgen_user_account_rlt
(
    id           BIGSERIAL   not null,
    user_name    varchar(50) not null,
    account_name varchar(50) not null,
    role         varchar(10) not null default '',
    create_at    TIMESTAMPTZ not null default now(),
    update_at    TIMESTAMPTZ not null default now(),
    PRIMARY KEY (id),
    CONSTRAINT uq_letsgen_user_account_rlt UNIQUE (user_name, account_name)
);
CREATE INDEX idx_letsgen_user_account_rlt_create_at ON letsgen_user_account_rlt (create_at);
CREATE INDEX idx_letsgen_user_account_rlt_update_at ON letsgen_user_account_rlt (update_at);

comment on table letsgen_user_account_rlt is '用户-计费账号关系表';
comment on column letsgen_user_account_rlt.id is '主键';
comment on column letsgen_user_account_rlt.user_name is '用户名';
comment on column letsgen_user_account_rlt.account_name is '计费账号名';
comment on column letsgen_user_account_rlt.role is '用户在计费账号下的角色:admin,normal';
comment on column letsgen_user_account_rlt.create_at is '创建时间';
comment on column letsgen_user_account_rlt.update_at is '更新时间';

-- 鉴权 token 表 letsgen_account_apikey
create table letsgen_account_apikey
(
    id            BIGSERIAL    not null,
    account_name  varchar(50)  not null,
    apikey_name   varchar(50)  not null default '',
    apikey_value  varchar(100) not null default '',
    apikey_status varchar(10)  not null default '',
    note          text         not null default '',
    create_at     TIMESTAMPTZ  not null default now(),
    update_at     TIMESTAMPTZ  not null default now(),
    PRIMARY KEY (id),
    CONSTRAINT uq_letsgen_account_token UNIQUE (account_name, apikey_name),
    CONSTRAINT uq_apikey_value UNIQUE (apikey_value)
);
-- ALTER table letsgen_account_apikey
--     ADD CONSTRAINT uq_apikey_value UNIQUE (apikey_value);
comment on table letsgen_account_apikey is '计费账号鉴权 apikey 表';
comment on column letsgen_account_apikey.id is '主键';
comment on column letsgen_account_apikey.account_name is '计费账号名';
comment on column letsgen_account_apikey.apikey_name is 'apikey 名称';
comment on column letsgen_account_apikey.apikey_value is 'apikey 值,加密的值';
comment on column letsgen_account_apikey.apikey_status is 'token 状态:ok,disabled';
comment on column letsgen_account_apikey.note is 'token 备注';
comment on column letsgen_account_apikey.create_at is '创建时间';
comment on column letsgen_account_apikey.update_at is '更新时间';

-- 钱包表 letsgen_wallet
create table letsgen_wallet
(
    id             BIGSERIAL       not null,
    account_name   varchar(50)     not null,
    currency_type  varchar(20)     not null default '',
    cur_balance    numeric(20, 12) not null default 0.0,
    summary_charge numeric(20, 12) not null default 0.0,
    wallet_status  varchar(10)     not null default '',
    note           text            not null default '',
    create_at      TIMESTAMPTZ     not null default now(),
    update_at      TIMESTAMPTZ     not null default now(),
    PRIMARY KEY (id),
    CONSTRAINT uq_letsgen_wallet UNIQUE (account_name, currency_type)
);

comment on table letsgen_wallet is '计费账号钱包表';
comment on column letsgen_wallet.id is '主键';
comment on column letsgen_wallet.account_name is '计费账号名';
comment on column letsgen_wallet.currency_type is '币种类型:USD,CNY,EUR等';
comment on column letsgen_wallet.cur_balance is '当前余额';
comment on column letsgen_wallet.summary_charge is '累计充值金额';
comment on column letsgen_wallet.wallet_status is '钱包状态:ok,disabled';
comment on column letsgen_wallet.note is '钱包备注';
comment on column letsgen_wallet.create_at is '创建时间';
comment on column letsgen_wallet.update_at is '更新时间';

-- 模型表 letsgen_model
create table letsgen_model
(
    id                 BIGSERIAL          not null,
    model_name         varchar(50) UNIQUE not null default '',           -- 模型名称,格式为 provider/model_name,如 azure/gpt-4o-24-08-06
    model_type         varchar(20)        not null default '',           -- 模型类型: generate, embedding, rerank
    model_status       varchar(10)        not null default '',           -- 模型状态: ok, waiting, disabled, deprecated
    provider           varchar(20)        not null default '',           -- 接入厂商
    support_tools      smallint           not null default 0,            -- 是否支持工具调用
    support_non_stream smallint           not null default 1,            -- 是否支持非流式响应
    support_stream     smallint           not null default 1,            -- 是否支持流式响应
    support_reasoning  smallint           not null default 0,            -- 是否支持推理
    input_modalities   varchar(100)       not null default '',           -- 支持的输入模态: text, image, audio, video
    output_modalities  varchar(100)       not null default '',           -- 支持的输出模态: text, image, audio, video
    model_version      varchar(20)        not null default '',           -- 模型版本
    expire_date        TIMESTAMPTZ        not null default '9999-12-31', -- 模型过期时间
    model_desc         text               not null default '',           -- 模型描述
    param_support_info text               not null default '',           -- 支持的控制参数,json格式
    token_len_info     text               not null default '',           -- token长度支持,json格式
    price_info         text               not null default '',           -- 价格信息,json格式
    reference_urls     text               not null default '',           -- 相关链接,包括价格/参数支持/quota,json格式
    note               text               not null default '',
    create_at          TIMESTAMPTZ        not null default now(),
    update_at          TIMESTAMPTZ        not null default now(),
    PRIMARY KEY (id)
);
comment on table letsgen_model is '模型信息表';
comment on column letsgen_model.id is '主键';
comment on column letsgen_model.model_name is '模型名称,格式为 provider/model_name,如 azure/gpt-4o-24-08-06';
comment on column letsgen_model.model_type is '模型类型: generate, embedding, rerank';
comment on column letsgen_model.model_status is '模型状态: ok, waiting, disabled, deprecated';
comment on column letsgen_model.provider is '接入厂商';
comment on column letsgen_model.support_tools is '是否支持工具调用,0:不支持,1:支持';
comment on column letsgen_model.support_non_stream is '是否支持非流式响应,0:不支持,1:支持';
comment on column letsgen_model.support_stream is '是否支持流式响应,0:不支持,1:支持';
comment on column letsgen_model.support_reasoning is '是否支持推理,0:不支持,1:支持';
comment on column letsgen_model.input_modalities is '支持的输入模态: text, image, audio, video';
comment on column letsgen_model.output_modalities is '支持的输出模态: text, image, audio, video';
comment on column letsgen_model.model_version is '模型版本';
comment on column letsgen_model.expire_date is '模型过期时间';
comment on column letsgen_model.model_desc is '模型描述';
comment on column letsgen_model.param_support_info is '支持的控制参数,json格式';
comment on column letsgen_model.token_len_info is 'token长度支持,json格式';
comment on column letsgen_model.price_info is '价格信息,json格式';
comment on column letsgen_model.reference_urls is '相关链接,包括价格/参数支持/quota,json格式';
comment on column letsgen_model.note is '模型备注';
comment on column letsgen_model.create_at is '创建时间';
comment on column letsgen_model.update_at is '更新时间';

-- 账号模型权限表 letsgen_account_model_rlt
create table letsgen_account_model_rlt
(
    id               BIGSERIAL   not null,
    account_name     varchar(50) not null default '', -- 计费账号名
    model_name       varchar(50) not null default '', -- 模型名称
    apply_user_name  varchar(50) not null default '', -- 申请用户
    rpd_limit        integer     not null default -1, -- 周期内请求数限制-请求次数
    rpd_duration     integer     not null default 60, -- 周期内请求数限制-时间周期,单位:秒
    tpd_limit        integer     not null default -1, -- 周期内 token 数限制 - token 数
    tpd_duration     integer     not null default 60, -- 周期内 token 数限制 - 时间周期,单位:秒
    concurrent_limit integer     not null default -1, -- 并发请求数限制
    create_at        TIMESTAMPTZ not null default now(),
    update_at        TIMESTAMPTZ not null default now(),
    PRIMARY KEY (id),
    CONSTRAINT uq_letsgen_account_model_rlt UNIQUE (account_name, model_name)
);
create index idx_letsgen_account_model_rlt_account_name ON letsgen_account_model_rlt (account_name);
create index idx_letsgen_account_model_rlt_model_name ON letsgen_account_model_rlt (model_name);
create index idx_letsgen_account_model_rlt_apply_user_name ON letsgen_account_model_rlt (apply_user_name);

comment on table letsgen_account_model_rlt is '计费账号模型权限表';
comment on column letsgen_account_model_rlt.id is '主键';
comment on column letsgen_account_model_rlt.account_name is '计费账号名';
comment on column letsgen_account_model_rlt.model_name is '模型名称';
comment on column letsgen_account_model_rlt.apply_user_name is '申请用户';
comment on column letsgen_account_model_rlt.rpd_limit is '周期内请求数限制-请求次数';
comment on column letsgen_account_model_rlt.rpd_duration is '周期内请求数限制-时间周期,单位:秒';
comment on column letsgen_account_model_rlt.tpd_limit is '周期内 token 数限制 - token 数';
comment on column letsgen_account_model_rlt.tpd_duration is '周期内 token 数限制 - 时间周期,单位:秒';
comment on column letsgen_account_model_rlt.concurrent_limit is '并发请求数限制';
comment on column letsgen_account_model_rlt.create_at is '创建时间';
comment on column letsgen_account_model_rlt.update_at is '更新时间';

-- 接入点凭证表 letsgen_provider_credential
create table letsgen_provider_credential
(
    id                BIGSERIAL   not null,
    provider_name     varchar(50) not null default '',                    -- 接入厂商名
    credential_name   varchar(50) not null default '',                    -- 凭证名称
    credential_type   varchar(20) not null default '',                    -- 凭证类型: api_key, credential_file 等
    credential_value  text        not null default '',                    -- 凭证值,加密的值
    credential_status varchar(10) not null default '',                    -- 凭证状态: ok, disabled
    expire_at         TIMESTAMPTZ not null default '9999-12-31 23:59:59', -- 凭证过期时间
    create_user       varchar(50) not null default '',                    -- 创建者用户名
    note              text        not null default '',
    create_at         TIMESTAMPTZ not null default now(),
    update_at         TIMESTAMPTZ not null default now(),
    PRIMARY KEY (id),
    CONSTRAINT uq_letsgen_provider_credential UNIQUE (provider_name, credential_name)
);
comment on table letsgen_provider_credential is '接入点凭证表';
comment on column letsgen_provider_credential.id is '主键';
comment on column letsgen_provider_credential.provider_name is '接入厂商名';
comment on column letsgen_provider_credential.credential_name is '凭证名称';
comment on column letsgen_provider_credential.credential_type is '凭证类型: api_key, credential_file';
comment on column letsgen_provider_credential.credential_value is '凭证值,加密的值';
comment on column letsgen_provider_credential.credential_status is '凭证状态: ok, disabled';
comment on column letsgen_provider_credential.expire_at is '凭证过期时间';
comment on column letsgen_provider_credential.create_user is '创建者用户名';
comment on column letsgen_provider_credential.note is '凭证备注';
comment on column letsgen_account_model_rlt.create_at is '创建时间';
comment on column letsgen_account_model_rlt.update_at is '更新时间';

-- 接入点表 letsgen_provider_endpoint
create table letsgen_provider_endpoint
(
    id                 BIGSERIAL     not null,
    provider_name      varchar(50)   not null default '', -- 接入厂商名
    endpoint_name      varchar(50)   not null default '', -- endpoint 名称
    credential_name1   varchar(50)   not null default '', -- 接入点使用的凭证名称1
    credential_name2   varchar(50)   not null default '', -- 接入点使用的凭证名称2
    endpoint_status    varchar(10)   not null default '', -- endpoint 状态: ok, down
    endpoint_baseurl   varchar(1024) not null default '', -- endpoint 基础路径
    endpoint_region    varchar(50)   not null default '', -- endpoint 区域代号
    endpoint_proxies   text          not null default '', -- endpoint 使用的代理(多个)
    api_format         varchar(50)   not null default '', -- 接口格式
    endpoint_path_info text          not null default '', -- endpoint path信息. 支持哪些路径,健康检查方式等
    endpoint_quota     text          not null default '', -- endpoint 容量. rpm/tpm/ifr
    note               text          not null default '',
    create_at          TIMESTAMPTZ   not null default now(),
    update_at          TIMESTAMPTZ   not null default now(),
    PRIMARY KEY (id),
    CONSTRAINT uq_letsgen_provider_endpoint UNIQUE (provider_name, endpoint_name)
);
comment on table letsgen_provider_endpoint is '厂商接入点表';
comment on column letsgen_provider_endpoint.id is '主键';
comment on column letsgen_provider_endpoint.provider_name is '接入厂商名';
comment on column letsgen_provider_endpoint.endpoint_name is 'endpoint 名称';
comment on column letsgen_provider_endpoint.credential_name1 is '接入点使用的凭证名称1';
comment on column letsgen_provider_endpoint.credential_name2 is '接入点使用的凭证名称2';
comment on column letsgen_provider_endpoint.endpoint_status is 'endpoint 状态: ok, down';
comment on column letsgen_provider_endpoint.endpoint_baseurl is 'endpoint 基础路径';
comment on column letsgen_provider_endpoint.endpoint_region is 'endpoint 区域代号';
comment on column letsgen_provider_endpoint.endpoint_proxies is 'endpoint 使用的代理(多个)';
comment on column letsgen_provider_endpoint.api_format is '接口格式';
comment on column letsgen_provider_endpoint.endpoint_path_info is 'endpoint path信息. 支持哪些路径,健康检查方式等';
comment on column letsgen_provider_endpoint.endpoint_quota is 'endpoint 容量. rpm/tpm/ifr';
comment on column letsgen_provider_endpoint.note is '接入点备注';
comment on column letsgen_provider_endpoint.create_at is '创建时间';
comment on column letsgen_provider_endpoint.update_at is '更新时间';

-- 模型-接入点关系表 letsgen_model_endpoint_rlt
drop table letsgen_model_endpoint_rlt;
create table letsgen_model_endpoint_rlt
(
    id                BIGSERIAL   not null,
    model_name        varchar(50) not null default '', -- 模型名称
    provider_name     varchar(50) not null default '', -- 接入厂商名
    endpoint_name     varchar(50) not null default '', -- endpoint 名称
    provider_model_id varchar(50) not null default '', -- 厂商侧模型代号
    provider_params   text        not null default '', -- 厂商侧额外调用参数
    m_edp_status      varchar(10) not null default '', -- 是否对该摸清启用这个 endpoint: ok, down
    rpd_limit         integer     not null default -1, -- 周期内请求数限制-请求次数
    rpd_duration      integer     not null default 60, -- 周期内请求数限制-时间周期,单位:秒
    tpd_limit         integer     not null default -1, -- 周期内 token 数限制 - token 数
    tpd_duration      integer     not null default 60, -- 周期内 token 数限制 - 时间周期,单位:秒
    ifr_limit         integer     not null default -1, -- 并发请求数(in-flight request)限制
    note              text        not null default '',
    create_at         TIMESTAMPTZ not null default now(),
    update_at         TIMESTAMPTZ not null default now(),
    PRIMARY KEY (id),
    CONSTRAINT uq_letsgen_model_endpoint UNIQUE (model_name, provider_name, endpoint_name)
);
comment on table letsgen_model_endpoint_rlt is '模型-接入点表';
comment on column letsgen_model_endpoint_rlt.id is '主键';
comment on column letsgen_model_endpoint_rlt.model_name is '模型名称';
comment on column letsgen_model_endpoint_rlt.provider_name is '接入厂商名';
comment on column letsgen_model_endpoint_rlt.endpoint_name is 'endpoint 名称';
comment on column letsgen_model_endpoint_rlt.provider_model_id is '厂商侧模型代号';
comment on column letsgen_model_endpoint_rlt.provider_params is '厂商侧额外调用参数';
comment on column letsgen_model_endpoint_rlt.m_edp_status is '是否对该摸清启用这个 endpoint: ok, down';
comment on column letsgen_model_endpoint_rlt.rpd_limit is '周期内请求数限制-请求次数';
comment on column letsgen_model_endpoint_rlt.rpd_duration is '周期内请求数限制-时间周期,单位:秒';
comment on column letsgen_model_endpoint_rlt.tpd_limit is '周期内 token 数限制 - token 数';
comment on column letsgen_model_endpoint_rlt.tpd_duration is '周期内 token 数限制 - 时间周期,单位:秒';
comment on column letsgen_model_endpoint_rlt.ifr_limit is '并发请求数(in-flight request)限制';
comment on column letsgen_model_endpoint_rlt.note is '模型-接入点备注';
comment on column letsgen_model_endpoint_rlt.create_at is '创建时间';
comment on column letsgen_model_endpoint_rlt.update_at is '更新时间';

-- 用户(n)-(n)计费账号(1)-(n)ApiKey
-- 账号(1)-(n)钱包, 每个币种一个钱包
-- 账号(n)-(n)模型, 关系表里加: 模态权限, 限流rpm/tpm/concurrent
-- 模型信息表(n)-(n)接入点(n)-(n)接入凭证
