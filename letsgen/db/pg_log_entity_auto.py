from typing import Optional
import datetime

from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, PrimaryKeyConstraint, String, Text, UniqueConstraint, text
from sqlmodel import Field, SQLModel

class LlmApiModelCallStat(SQLModel, table=True):
    __tablename__ = 'llm_api_model_call_stat'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'call_time_hour', name='llm_api_model_call_stat_pkey'),
        UniqueConstraint('account_name', 'model_name', 'call_time_hour', name='uq_llm_api_model_call_stat'),
        Index('idx_llm_api_model_call_stat_account_name', 'account_name'),
        Index('idx_llm_api_model_call_stat_call_time_hour', 'call_time_hour'),
        Index('idx_llm_api_model_call_stat_model_name', 'model_name'),
        Index('idx_llm_api_model_call_stat_period_last_call_at', 'period_last_call_at'),
        Index('llm_api_model_call_stat_call_time_hour_idx', 'call_time_hour'),
        {'comment': 'llm模型调用统计表'}
    )

    id: int = Field(sa_column=Column('id', BigInteger, primary_key=True, autoincrement=True, comment='主键'))
    account_name: str = Field(sa_column=Column('account_name', String(50), nullable=False, server_default=text("''::character varying"), comment='计费账号名'))
    model_name: str = Field(sa_column=Column('model_name', String(50), nullable=False, server_default=text("''::character varying"), comment='模型名称'))
    call_time_hour: datetime.datetime = Field(sa_column=Column('call_time_hour', DateTime(True), primary_key=True, server_default=text("'2000-01-01 08:00:00+08'::timestamp with time zone"), comment='调用发起时间对应的开始小时'))
    period_last_call_at: datetime.datetime = Field(sa_column=Column('period_last_call_at', DateTime(True), nullable=False, server_default=text("'2000-01-01 08:00:00+08'::timestamp with time zone"), comment='统计周期内最后一次完成调用的时间'))
    call_num: int = Field(sa_column=Column('call_num', Integer, nullable=False, server_default=text('0'), comment='统计周期内调用次数'))
    failed_call_num: int = Field(sa_column=Column('failed_call_num', Integer, nullable=False, server_default=text('0'), comment='统计周期内失败调用次数'))
    input_token_num: int = Field(sa_column=Column('input_token_num', Integer, nullable=False, server_default=text('0'), comment='统计周期内输入token数'))
    cached_token_num: int = Field(sa_column=Column('cached_token_num', Integer, nullable=False, server_default=text('0'), comment='统计周期内缓存token数'))
    output_token_num: int = Field(sa_column=Column('output_token_num', Integer, nullable=False, server_default=text('0'), comment='统计周期内输出token数'))
    reason_token_num: int = Field(sa_column=Column('reason_token_num', Integer, nullable=False, server_default=text('0'), comment='统计周期内推理token数'))
    create_at: datetime.datetime = Field(sa_column=Column('create_at', DateTime(True), nullable=False, server_default=text('now()'), comment='创建时间'))
    update_at: datetime.datetime = Field(sa_column=Column('update_at', DateTime(True), nullable=False, server_default=text('now()'), comment='更新时间'))


class LlmApiRequestBodyLog(SQLModel, table=True):
    __tablename__ = 'llm_api_request_body_log'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'log_time', name='llm_api_request_body_log_pkey'),
        Index('llm_api_request_body_log_log_time_idx', 'log_time'),
        {'comment': 'llm请求体信息,只含请求体大文本不含控制参数'}
    )

    id: int = Field(sa_column=Column('id', BigInteger, primary_key=True, comment='主键'))
    log_time: datetime.datetime = Field(sa_column=Column('log_time', DateTime(True), primary_key=True, server_default=text('now()'), comment='入库记录时间'))
    account_name: str = Field(sa_column=Column('account_name', String(50), nullable=False, server_default=text("''::character varying"), comment='账号名'))
    model_name: str = Field(sa_column=Column('model_name', String(50), nullable=False, server_default=text("''::character varying"), comment='模型名'))
    request_body: str = Field(sa_column=Column('request_body', Text, nullable=False, server_default=text("''::text"), comment='请求体'))
    request_header: str = Field(sa_column=Column('request_header', Text, nullable=False, server_default=text("''::text"), comment='向厂商发送的请求 header'))
    reply_body: str = Field(sa_column=Column('reply_body', Text, nullable=False, server_default=text("''::text"), comment='厂商响应体'))
    reply_header: str = Field(sa_column=Column('reply_header', Text, nullable=False, server_default=text("''::text"), comment='厂商响应头'))


class LlmApiRequestMetaLog(SQLModel, table=True):
    __tablename__ = 'llm_api_request_meta_log'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'log_time', name='llm_api_request_meta_log_pkey'),
        Index('llm_api_request_meta_log_log_time_idx', 'log_time'),
        {'comment': 'llm请求元信息表,只含参数不含prompt和reply'}
    )

    id: int = Field(sa_column=Column('id', BigInteger, primary_key=True, comment='主键'))
    log_time: datetime.datetime = Field(sa_column=Column('log_time', DateTime(True), primary_key=True, server_default=text('now()'), comment='入库记录时间'))
    account_name: str = Field(sa_column=Column('account_name', String(50), nullable=False, server_default=text("''::character varying"), comment='账号名'))
    model_name: str = Field(sa_column=Column('model_name', String(50), nullable=False, server_default=text("''::character varying"), comment='模型名'))
    gen_api_path: str = Field(sa_column=Column('gen_api_path', String(1000), nullable=False, server_default=text("''::character varying"), comment='letsgen 接口路径'))
    interact_mode: str = Field(sa_column=Column('interact_mode', String(10), nullable=False, server_default=text("''::character varying"), comment='交互模式:stream,single'))
    provider_name: str = Field(sa_column=Column('provider_name', String(50), nullable=False, server_default=text("''::character varying"), comment='接入厂商名'))
    gen_trace_id: str = Field(sa_column=Column('gen_trace_id', String(50), nullable=False, server_default=text("''::character varying"), comment='trace_id'))
    request_id: str = Field(sa_column=Column('request_id', String(100), nullable=False, server_default=text("''::character varying"), comment='厂商提供的 request id'))
    request_body_meta: str = Field(sa_column=Column('request_body_meta', Text, nullable=False, server_default=text("''::text"), comment='请求体元数据'))
    reply_body_meta: str = Field(sa_column=Column('reply_body_meta', Text, nullable=False, server_default=text("''::text"), comment='响应体元数据'))
    request_in_time: datetime.datetime = Field(sa_column=Column('request_in_time', DateTime(True), nullable=False, server_default=text("'2000-01-01 08:00:00+08'::timestamp with time zone"), comment='letsgen 接到的时间'))
    provider_in_time: datetime.datetime = Field(sa_column=Column('provider_in_time', DateTime(True), nullable=False, server_default=text("'2000-01-01 08:00:00+08'::timestamp with time zone"), comment='向厂商发起请求的时间'))
    provider_end_time: datetime.datetime = Field(sa_column=Column('provider_end_time', DateTime(True), nullable=False, server_default=text("'2000-01-01 08:00:00+08'::timestamp with time zone"), comment='厂商结束响应时间'))
    request_out_time: datetime.datetime = Field(sa_column=Column('request_out_time', DateTime(True), nullable=False, server_default=text("'2000-01-01 08:00:00+08'::timestamp with time zone"), comment='letsgen 发送完响应时间'))
    provider_region: Optional[str] = Field(default=None, sa_column=Column('provider_region', String(50), comment='接入厂商服务区,部分厂商没有区的概念'))
    first_token_time: Optional[datetime.datetime] = Field(default=None, sa_column=Column('first_token_time', DateTime(True), comment='收到首 token 响应时间,仅对stream有值'))
