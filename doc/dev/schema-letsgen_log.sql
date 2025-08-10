CREATE DATABASE letsgen_log
    WITH ENCODING 'UTF8'
    LC_COLLATE = 'C.UTF-8'
    LC_CTYPE = 'C.UTF-8'
;

-- 请求元信息日志表
CREATE TABLE llm_api_request_meta_log
(
    id                BIGSERIAL    not null,
    log_time          TIMESTAMPTZ  not null default now(),
    account_name      varchar(50)  not null default '',
    model_name        varchar(50)  not null default '',
    gen_api_path      varchar(100) not null default '',
    interact_mode     varchar(10)  not null default '',
    provider_name     varchar(50)  not null default '',
    provider_region   varchar(50)  null,
    gen_trace_id      varchar(50)  not null default '',
    request_id        varchar(100) not null default '',
    request_body_meta text         not null default '',
    reply_body_meta   text         not null default '',
    request_in_time   TIMESTAMPTZ  not null default '2000-01-01T00:00:00Z',
    provider_in_time  TIMESTAMPTZ  not null default '2000-01-01T00:00:00Z',
    first_token_time  TIMESTAMPTZ  null,
    provider_end_time TIMESTAMPTZ  not null default '2000-01-01T00:00:00Z',
    request_out_time  TIMESTAMPTZ  not null default '2000-01-01T00:00:00Z',
    PRIMARY KEY (id, log_time)
)
    WITH (
        timescaledb.hypertable,
        timescaledb.partition_column = 'log_time',
        timescaledb.segmentby = 'account_name,model_name',
        timescaledb.compress = true
        );
COMMENT ON TABLE llm_api_request_meta_log IS 'llm请求元信息表,只含参数不含prompt和reply';
COMMENT ON COLUMN llm_api_request_meta_log.id IS '主键';
COMMENT ON COLUMN llm_api_request_meta_log.log_time IS '入库记录时间';
COMMENT ON COLUMN llm_api_request_meta_log.account_name IS '账号名';
COMMENT ON COLUMN llm_api_request_meta_log.model_name IS '模型名';
COMMENT ON COLUMN llm_api_request_meta_log.gen_api_path IS 'letsgen 接口路径';
COMMENT ON COLUMN llm_api_request_meta_log.interact_mode IS '交互模式:stream,single';
COMMENT ON COLUMN llm_api_request_meta_log.provider_name IS '接入厂商名';
COMMENT ON COLUMN llm_api_request_meta_log.provider_region IS '接入厂商服务区,部分厂商没有区的概念';
COMMENT ON COLUMN llm_api_request_meta_log.gen_trace_id IS 'trace_id';
COMMENT ON COLUMN llm_api_request_meta_log.request_id IS '厂商提供的 request id';
COMMENT ON COLUMN llm_api_request_meta_log.request_body_meta IS '请求体元数据';
COMMENT ON COLUMN llm_api_request_meta_log.reply_body_meta IS '响应体元数据';
COMMENT ON COLUMN llm_api_request_meta_log.request_in_time IS 'letsgen 接到的时间';
COMMENT ON COLUMN llm_api_request_meta_log.provider_in_time IS '向厂商发起请求的时间';
COMMENT ON COLUMN llm_api_request_meta_log.first_token_time IS '收到首 token 响应时间,仅对stream有值';
COMMENT ON COLUMN llm_api_request_meta_log.provider_end_time IS '厂商结束响应时间';
COMMENT ON COLUMN llm_api_request_meta_log.request_out_time IS 'letsgen 发送完响应时间';

-- 请求体日志表
CREATE TABLE llm_api_request_body_log
(
    id             BIGINT      not null,
    log_time       TIMESTAMPTZ not null default now(),
    account_name   varchar(50) not null default '',
    model_name     varchar(50) not null default '',
    request_body   text        not null default '',
    request_header text        not null default '',
    reply_body     text        not null default '',
    reply_header   text        not null default '',
    PRIMARY KEY (id, log_time)
)
    WITH (
        timescaledb.hypertable,
        timescaledb.partition_column = 'log_time',
        timescaledb.segmentby = 'account_name,model_name',
        timescaledb.compress = true
        );
COMMENT ON TABLE llm_api_request_body_log IS 'llm请求体信息,只含请求体大文本不含控制参数';
COMMENT ON COLUMN llm_api_request_body_log.id IS '主键';
COMMENT ON COLUMN llm_api_request_body_log.log_time IS '入库记录时间';
COMMENT ON COLUMN llm_api_request_body_log.account_name IS '账号名';
COMMENT ON COLUMN llm_api_request_body_log.model_name IS '模型名';
COMMENT ON COLUMN llm_api_request_body_log.request_body IS '请求体';
COMMENT ON COLUMN llm_api_request_body_log.request_header IS '向厂商发送的请求 header';
COMMENT ON COLUMN llm_api_request_body_log.reply_body IS '厂商响应体';
COMMENT ON COLUMN llm_api_request_body_log.reply_header IS '厂商响应头';
