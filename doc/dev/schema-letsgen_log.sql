CREATE DATABASE letsgen_log
    WITH ENCODING 'UTF8'
    LC_COLLATE = 'C.UTF-8'
    LC_CTYPE = 'C.UTF-8'
;
ALTER DATABASE letsgen_log SET timezone = 'Asia/Shanghai';

\connect letsgen_log

SET pg_textsearch.default_limit = 1500;

-- 调用统计表 llm_api_model_call_stat
create table llm_api_model_call_stat
(
    id                  BIGSERIAL   not null,
    account_name        varchar(50) not null default '',                    -- 计费账号名
    model_id            varchar(50) not null default '',                    -- 模型名称
    call_time_hour      TIMESTAMPTZ not null default '2000-01-01 00:00:00', -- 调用发起时间对应的开始小时
    period_last_call_at TIMESTAMPTZ not null default '2000-01-01 00:00:00', -- 统计周期内最后一次完成调用时间
    call_num            integer     not null default 0,                     -- 调用次数
    failed_call_num     integer     not null default 0,                     -- 失败调用次数
    input_token_num     integer     not null default 0,                     -- 输入token数
    cached_token_num    integer     not null default 0,                     -- 缓存token数
    output_token_num    integer     not null default 0,                     -- 输出token数
    reason_token_num    integer     not null default 0,                     -- 推理token数
    create_at           TIMESTAMPTZ not null default now(),
    update_at           TIMESTAMPTZ not null default now(),
    PRIMARY KEY (id, call_time_hour),
    CONSTRAINT uq_llm_api_model_call_stat UNIQUE (account_name, model_id, call_time_hour)
)
    WITH (
        timescaledb.hypertable,
        timescaledb.partition_column = 'call_time_hour',
        timescaledb.segmentby = 'account_name, model_id',
        timescaledb.chunk_interval = '1 days',
        timescaledb.compress = true
        );
create index idx_llm_api_model_call_stat_account_name ON llm_api_model_call_stat (account_name);
create index idx_llm_api_model_call_stat_model_id ON llm_api_model_call_stat (model_id);
create index idx_llm_api_model_call_stat_call_time_hour ON llm_api_model_call_stat (call_time_hour);
create index idx_llm_api_model_call_stat_period_last_call_at ON llm_api_model_call_stat (period_last_call_at);

comment on table llm_api_model_call_stat is 'llm模型调用统计表';
comment on column llm_api_model_call_stat.id is '主键';
comment on column llm_api_model_call_stat.account_name is '计费账号名';
comment on column llm_api_model_call_stat.model_id is '模型名称';
comment on column llm_api_model_call_stat.call_time_hour is '调用发起时间对应的开始小时';
comment on column llm_api_model_call_stat.period_last_call_at is '统计周期内最后一次完成调用的时间';
comment on column llm_api_model_call_stat.call_num is '统计周期内调用次数';
comment on column llm_api_model_call_stat.failed_call_num is '统计周期内失败调用次数';
comment on column llm_api_model_call_stat.input_token_num is '统计周期内输入token数';
comment on column llm_api_model_call_stat.cached_token_num is '统计周期内缓存token数';
comment on column llm_api_model_call_stat.output_token_num is '统计周期内输出token数';
comment on column llm_api_model_call_stat.reason_token_num is '统计周期内推理token数';
comment on column llm_api_model_call_stat.create_at is '创建时间';
comment on column llm_api_model_call_stat.update_at is '更新时间';

-- 请求元信息日志表
CREATE TABLE llm_api_request_meta_log
(
    id                BIGSERIAL     not null,
    log_time          TIMESTAMPTZ   not null default now(),
    account_name      varchar(50)   not null default '',
    model_id          varchar(50)   not null default '',
    gen_api_path      varchar(1000) not null default '',
    gen_req_id        varchar(100)  not null default '',
    gen_trace_id      varchar(50)   not null default '',
    interact_mode     varchar(10)   not null default '',
    provider_name     varchar(50)   not null default '',
    provider_region   varchar(50)   null,
    provider_req_id   varchar(100)  not null default '',
    request_body_meta text          not null default '',
    reply_body_meta   text          not null default '',
    request_in_time   TIMESTAMPTZ   not null default '2000-01-01T00:00:00Z',
    provider_in_time  TIMESTAMPTZ   not null default '2000-01-01T00:00:00Z',
    first_token_time  TIMESTAMPTZ   null,
    provider_end_time TIMESTAMPTZ   not null default '2000-01-01T00:00:00Z',
    response_out_time TIMESTAMPTZ   not null default '2000-01-01T00:00:00Z',
    PRIMARY KEY (id, log_time)
)
    WITH (
        timescaledb.hypertable,
        timescaledb.partition_column = 'log_time',
        timescaledb.segmentby = 'account_name,model_id',
        timescaledb.chunk_interval = '1 days',
        timescaledb.compress = true
        );
COMMENT ON TABLE llm_api_request_meta_log IS 'llm请求元信息表,只含参数不含prompt和reply';
COMMENT ON COLUMN llm_api_request_meta_log.id IS '主键';
COMMENT ON COLUMN llm_api_request_meta_log.log_time IS '入库记录时间';
COMMENT ON COLUMN llm_api_request_meta_log.account_name IS '账号名';
COMMENT ON COLUMN llm_api_request_meta_log.model_id IS '模型名';
COMMENT ON COLUMN llm_api_request_meta_log.gen_api_path IS 'letsgen 接口路径';
COMMENT ON COLUMN llm_api_request_meta_log.gen_req_id IS 'letsgen 生成的请求 id';
COMMENT ON COLUMN llm_api_request_meta_log.interact_mode IS '交互模式:stream,single';
COMMENT ON COLUMN llm_api_request_meta_log.provider_name IS '接入厂商名';
COMMENT ON COLUMN llm_api_request_meta_log.provider_region IS '接入厂商服务区,部分厂商没有区的概念';
COMMENT ON COLUMN llm_api_request_meta_log.gen_trace_id IS 'trace_id';
COMMENT ON COLUMN llm_api_request_meta_log.provider_req_id IS '厂商提供的 request id';
COMMENT ON COLUMN llm_api_request_meta_log.request_body_meta IS '请求体元数据';
COMMENT ON COLUMN llm_api_request_meta_log.reply_body_meta IS '响应体元数据';
COMMENT ON COLUMN llm_api_request_meta_log.request_in_time IS 'letsgen 接到的时间';
COMMENT ON COLUMN llm_api_request_meta_log.provider_in_time IS '向厂商发起请求的时间';
COMMENT ON COLUMN llm_api_request_meta_log.first_token_time IS '收到首 token 响应时间,仅对stream有值';
COMMENT ON COLUMN llm_api_request_meta_log.provider_end_time IS '厂商结束响应时间';
COMMENT ON COLUMN llm_api_request_meta_log.response_out_time IS 'letsgen 发送完响应时间';

-- 请求体日志表
CREATE TABLE llm_api_request_body_log
(
    id             BIGINT        not null,
    log_time       TIMESTAMPTZ   not null default now(),
    account_name   varchar(50)   not null default '',
    model_id       varchar(50)   not null default '',
    gen_api_path   varchar(1000) not null default '',
    interact_mode  varchar(10)   not null default '',
    request_body   text          not null default '',
    request_header text          not null default '',
    reply_body     text          not null default '',
    reply_header   text          not null default '',
    PRIMARY KEY (id, log_time)
)
    WITH (
        timescaledb.hypertable,
        timescaledb.partition_column = 'log_time',
        timescaledb.segmentby = 'account_name,model_id',
        timescaledb.chunk_interval = '1 days',
        timescaledb.compress = true
        );
COMMENT ON TABLE llm_api_request_body_log IS 'llm请求体信息,只含请求体大文本不含控制参数';
COMMENT ON COLUMN llm_api_request_body_log.id IS '主键';
COMMENT ON COLUMN llm_api_request_body_log.log_time IS '入库记录时间';
COMMENT ON COLUMN llm_api_request_body_log.account_name IS '账号名';
COMMENT ON COLUMN llm_api_request_body_log.model_id IS '模型名';
COMMENT ON COLUMN llm_api_request_body_log.gen_api_path IS 'letsgen 接口路径';
COMMENT ON COLUMN llm_api_request_body_log.interact_mode IS '交互模式:stream,single';
COMMENT ON COLUMN llm_api_request_body_log.request_body IS '请求体';
COMMENT ON COLUMN llm_api_request_body_log.request_header IS '向厂商发送的请求 header';
COMMENT ON COLUMN llm_api_request_body_log.reply_body IS '厂商响应体';
COMMENT ON COLUMN llm_api_request_body_log.reply_header IS '厂商响应头';
