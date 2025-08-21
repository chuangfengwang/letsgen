CREATE DATABASE letsgen_db
    WITH ENCODING 'UTF8'
    LC_COLLATE = 'C.UTF-8'
    LC_CTYPE = 'C.UTF-8'
;

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
COMMENT ON COLUMN letsgen_user.user_status IS '用户状态:ok,disabled';
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
    id           BIGSERIAL    not null,
    account_name varchar(50)  not null,
    apikey_name   varchar(50)  not null default '',
    apikey_value        varchar(100) not null default '',
    apikey_status varchar(10)  not null default '',
    note         text         not null default '',
    create_at    TIMESTAMPTZ  not null default now(),
    update_at    TIMESTAMPTZ  not null default now(),
    PRIMARY KEY (id),
    CONSTRAINT uq_letsgen_account_token UNIQUE (account_name, apikey_name)
);
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
    supports_reasoning smallint           not null default 0,            -- 是否支持推理
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
comment on column letsgen_model.supports_reasoning is '是否支持推理,0:不支持,1:支持';
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
    id              BIGSERIAL   not null,
    account_name    varchar(50) not null default '', -- 计费账号名
    model_name      varchar(50) not null default '', -- 模型名称
    apply_user_name varchar(50) not null default '', -- 申请用户
    rpm_limit       integer     not null default 0,  -- 每分钟请求数限制
    tpm_limit       integer     not null default 0,  -- 每分钟 token 数限制
    concurrent      integer     not null default 0,  -- 并发请求数限制
    create_at       TIMESTAMPTZ not null default now(),
    update_at       TIMESTAMPTZ not null default now(),
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
comment on column letsgen_account_model_rlt.rpm_limit is '每分钟请求数限制';
comment on column letsgen_account_model_rlt.tpm_limit is '每分钟 token 数限制';
comment on column letsgen_account_model_rlt.concurrent is '并发请求数限制';
comment on column letsgen_account_model_rlt.create_at is '创建时间';
comment on column letsgen_account_model_rlt.update_at is '更新时间';

-- 调用统计表 letsgen_model_call_stat
create table letsgen_model_call_stat
(
    id                  BIGSERIAL   not null,
    account_name        varchar(50) not null default '',                    -- 计费账号名
    model_name          varchar(50) not null default '',                    -- 模型名称
    call_time_hour      TIMESTAMPTZ not null default '2000-01-01 00:00:00', -- 调用发起时间对应的开始小时
    period_last_call_at TIMESTAMPTZ not null default '2000-01-01 00:00:00', -- 统计周期内最后一次调用时间
    call_num            integer     not null default 0,                     -- 调用次数
    failed_call_num     integer     not null default 0,                     -- 失败调用次数
    input_token_num     integer     not null default 0,                     -- 输入token数
    cached_token_num    integer     not null default 0,                     -- 缓存token数
    output_token_num    integer     not null default 0,                     -- 输出token数
    reason_token_num    integer     not null default 0,                     -- 推理token数
    create_at           TIMESTAMPTZ not null default now(),
    update_at           TIMESTAMPTZ not null default now(),
    PRIMARY KEY (id),
    CONSTRAINT uq_letsgen_model_call_stat UNIQUE (account_name, model_name, call_time_hour)
);
create index idx_letsgen_model_call_stat_account_name ON letsgen_model_call_stat (account_name);
create index idx_letsgen_model_call_stat_model_name ON letsgen_model_call_stat (model_name);
create index idx_letsgen_model_call_stat_call_time_hour ON letsgen_model_call_stat (call_time_hour);
create index idx_letsgen_model_call_stat_period_last_call_at ON letsgen_model_call_stat (period_last_call_at);

comment on table letsgen_model_call_stat is '模型调用统计表';
comment on column letsgen_model_call_stat.id is '主键';
comment on column letsgen_model_call_stat.account_name is '计费账号名';
comment on column letsgen_model_call_stat.model_name is '模型名称';
comment on column letsgen_model_call_stat.call_time_hour is '调用发起时间对应的开始小时';
comment on column letsgen_model_call_stat.period_last_call_at is '统计周期内最后一次调用时间';
comment on column letsgen_model_call_stat.call_num is '统计周期内调用次数';
comment on column letsgen_model_call_stat.failed_call_num is '统计周期内失败调用次数';
comment on column letsgen_model_call_stat.input_token_num is '统计周期内输入token数';
comment on column letsgen_model_call_stat.cached_token_num is '统计周期内缓存token数';
comment on column letsgen_model_call_stat.output_token_num is '统计周期内输出token数';
comment on column letsgen_model_call_stat.reason_token_num is '统计周期内推理token数';
comment on column letsgen_model_call_stat.create_at is '创建时间';
comment on column letsgen_model_call_stat.update_at is '更新时间';

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
-- 模型接入点表 letsgen_model_endpoint


-- 用户(n)-(n)计费账号(1)-(n)token
-- 账号(1)-(n)钱包, 每个币种一个钱包
-- 账号(n)-(n)模型, 关系表里加: 模态权限, 限流rpm/tpm/concurrent
-- 模型信息表(n)-(n)接入点(n)-(n)接入凭证
