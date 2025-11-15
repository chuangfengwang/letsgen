import datetime
import decimal

from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, Numeric, PrimaryKeyConstraint, SmallInteger, String, Text, UniqueConstraint, text
from sqlmodel import Field, SQLModel

class LetsgenAccountApikey(SQLModel, table=True):
    __tablename__ = 'letsgen_account_apikey'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='letsgen_account_apikey_pkey'),
        UniqueConstraint('account_name', 'apikey_name', name='uq_letsgen_account_token'),
        UniqueConstraint('apikey_value', name='uq_apikey_value'),
        {'comment': '计费账号鉴权 apikey 表'}
    )

    id: int = Field(sa_column=Column('id', BigInteger, primary_key=True, comment='主键'))
    account_name: str = Field(sa_column=Column('account_name', String(50), nullable=False, comment='计费账号名'))
    apikey_name: str = Field(sa_column=Column('apikey_name', String(50), nullable=False, server_default=text("''::character varying"), comment='apikey 名称'))
    apikey_value: str = Field(sa_column=Column('apikey_value', String(100), nullable=False, server_default=text("''::character varying"), comment='apikey 值,加密的值'))
    apikey_status: str = Field(sa_column=Column('apikey_status', String(10), nullable=False, server_default=text("''::character varying"), comment='token 状态:ok,disabled'))
    note: str = Field(sa_column=Column('note', Text, nullable=False, server_default=text("''::text"), comment='token 备注'))
    create_at: datetime.datetime = Field(sa_column=Column('create_at', DateTime(True), nullable=False, server_default=text('now()'), comment='创建时间'))
    update_at: datetime.datetime = Field(sa_column=Column('update_at', DateTime(True), nullable=False, server_default=text('now()'), comment='更新时间'))


class LetsgenAccountModelRlt(SQLModel, table=True):
    __tablename__ = 'letsgen_account_model_rlt'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='letsgen_account_model_rlt_pkey'),
        UniqueConstraint('account_name', 'model_name', name='uq_letsgen_account_model_rlt'),
        Index('idx_letsgen_account_model_rlt_account_name', 'account_name'),
        Index('idx_letsgen_account_model_rlt_apply_user_name', 'apply_user_name'),
        Index('idx_letsgen_account_model_rlt_model_name', 'model_name'),
        {'comment': '计费账号模型权限表'}
    )

    id: int = Field(sa_column=Column('id', BigInteger, primary_key=True, comment='主键'))
    account_name: str = Field(sa_column=Column('account_name', String(50), nullable=False, server_default=text("''::character varying"), comment='计费账号名'))
    model_name: str = Field(sa_column=Column('model_name', String(50), nullable=False, server_default=text("''::character varying"), comment='模型名称'))
    apply_user_name: str = Field(sa_column=Column('apply_user_name', String(50), nullable=False, server_default=text("''::character varying"), comment='申请用户'))
    rpd_limit: int = Field(sa_column=Column('rpd_limit', Integer, nullable=False, server_default=text("'-1'::integer"), comment='周期内请求数限制-请求次数'))
    rpd_duration: int = Field(sa_column=Column('rpd_duration', Integer, nullable=False, server_default=text('60'), comment='周期内请求数限制-时间周期,单位:秒'))
    tpd_limit: int = Field(sa_column=Column('tpd_limit', Integer, nullable=False, server_default=text("'-1'::integer"), comment='周期内 token 数限制 - token 数'))
    tpd_duration: int = Field(sa_column=Column('tpd_duration', Integer, nullable=False, server_default=text('60'), comment='周期内 token 数限制 - 时间周期,单位:秒'))
    concurrent_limit: int = Field(sa_column=Column('concurrent_limit', Integer, nullable=False, server_default=text("'-1'::integer"), comment='并发请求数限制'))
    create_at: datetime.datetime = Field(sa_column=Column('create_at', DateTime(True), nullable=False, server_default=text('now()'), comment='创建时间'))
    update_at: datetime.datetime = Field(sa_column=Column('update_at', DateTime(True), nullable=False, server_default=text('now()'), comment='更新时间'))


class LetsgenBillAccount(SQLModel, table=True):
    __tablename__ = 'letsgen_bill_account'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='letsgen_bill_account_pkey'),
        UniqueConstraint('account_name', name='letsgen_bill_account_account_name_key'),
        Index('idx_letsgen_bill_account_create_at', 'create_at'),
        Index('idx_letsgen_bill_account_update_at', 'update_at'),
        {'comment': '计费账号表'}
    )

    id: int = Field(sa_column=Column('id', BigInteger, primary_key=True, comment='主键'))
    account_name: str = Field(sa_column=Column('account_name', String(50), nullable=False, server_default=text("''::character varying"), comment='计费账号名'))
    account_status: str = Field(sa_column=Column('account_status', String(10), nullable=False, server_default=text("''::character varying"), comment='计费账号状态:ok,disabled'))
    create_user_name: str = Field(sa_column=Column('create_user_name', String(50), nullable=False, server_default=text("''::character varying"), comment='创建者用户名'))
    note: str = Field(sa_column=Column('note', Text, nullable=False, server_default=text("''::text"), comment='账号备注'))
    create_at: datetime.datetime = Field(sa_column=Column('create_at', DateTime(True), nullable=False, server_default=text('now()'), comment='创建时间'))
    update_at: datetime.datetime = Field(sa_column=Column('update_at', DateTime(True), nullable=False, server_default=text('now()'), comment='更新时间'))


class LetsgenModel(SQLModel, table=True):
    __tablename__ = 'letsgen_model'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='letsgen_model_pkey'),
        UniqueConstraint('model_name', name='letsgen_model_model_name_key'),
        {'comment': '模型信息表'}
    )

    id: int = Field(sa_column=Column('id', BigInteger, primary_key=True, comment='主键'))
    model_name: str = Field(sa_column=Column('model_name', String(50), nullable=False, server_default=text("''::character varying"), comment='模型名称,格式为 provider/model_name,如 azure/gpt-4o-24-08-06'))
    model_type: str = Field(sa_column=Column('model_type', String(20), nullable=False, server_default=text("''::character varying"), comment='模型类型: generate, embedding, rerank'))
    model_status: str = Field(sa_column=Column('model_status', String(10), nullable=False, server_default=text("''::character varying"), comment='模型状态: ok, waiting, disabled, deprecated'))
    provider: str = Field(sa_column=Column('provider', String(20), nullable=False, server_default=text("''::character varying"), comment='接入厂商'))
    support_tools: int = Field(sa_column=Column('support_tools', SmallInteger, nullable=False, server_default=text('0'), comment='是否支持工具调用,0:不支持,1:支持'))
    support_non_stream: int = Field(sa_column=Column('support_non_stream', SmallInteger, nullable=False, server_default=text('1'), comment='是否支持非流式响应,0:不支持,1:支持'))
    support_stream: int = Field(sa_column=Column('support_stream', SmallInteger, nullable=False, server_default=text('1'), comment='是否支持流式响应,0:不支持,1:支持'))
    support_reasoning: int = Field(sa_column=Column('support_reasoning', SmallInteger, nullable=False, server_default=text('0'), comment='是否支持推理,0:不支持,1:支持'))
    input_modalities: str = Field(sa_column=Column('input_modalities', String(100), nullable=False, server_default=text("''::character varying"), comment='支持的输入模态: text, image, audio, video'))
    output_modalities: str = Field(sa_column=Column('output_modalities', String(100), nullable=False, server_default=text("''::character varying"), comment='支持的输出模态: text, image, audio, video'))
    model_version: str = Field(sa_column=Column('model_version', String(20), nullable=False, server_default=text("''::character varying"), comment='模型版本'))
    expire_date: datetime.datetime = Field(sa_column=Column('expire_date', DateTime(True), nullable=False, server_default=text("'9999-12-31 00:00:00+08'::timestamp with time zone"), comment='模型过期时间'))
    model_desc: str = Field(sa_column=Column('model_desc', Text, nullable=False, server_default=text("''::text"), comment='模型描述'))
    param_support_info: str = Field(sa_column=Column('param_support_info', Text, nullable=False, server_default=text("''::text"), comment='支持的控制参数,json格式'))
    token_len_info: str = Field(sa_column=Column('token_len_info', Text, nullable=False, server_default=text("''::text"), comment='token长度支持,json格式'))
    price_info: str = Field(sa_column=Column('price_info', Text, nullable=False, server_default=text("''::text"), comment='价格信息,json格式'))
    reference_urls: str = Field(sa_column=Column('reference_urls', Text, nullable=False, server_default=text("''::text"), comment='相关链接,包括价格/参数支持/quota,json格式'))
    note: str = Field(sa_column=Column('note', Text, nullable=False, server_default=text("''::text"), comment='模型备注'))
    create_at: datetime.datetime = Field(sa_column=Column('create_at', DateTime(True), nullable=False, server_default=text('now()'), comment='创建时间'))
    update_at: datetime.datetime = Field(sa_column=Column('update_at', DateTime(True), nullable=False, server_default=text('now()'), comment='更新时间'))


class LetsgenModelEndpointRlt(SQLModel, table=True):
    __tablename__ = 'letsgen_model_endpoint_rlt'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='letsgen_model_endpoint_rlt_pkey'),
        UniqueConstraint('model_name', 'provider_name', 'endpoint_name', name='uq_letsgen_model_endpoint'),
        {'comment': '模型-接入点表'}
    )

    id: int = Field(sa_column=Column('id', BigInteger, primary_key=True, comment='主键'))
    model_name: str = Field(sa_column=Column('model_name', String(50), nullable=False, server_default=text("''::character varying"), comment='模型名称'))
    provider_name: str = Field(sa_column=Column('provider_name', String(50), nullable=False, server_default=text("''::character varying"), comment='接入厂商名'))
    endpoint_name: str = Field(sa_column=Column('endpoint_name', String(50), nullable=False, server_default=text("''::character varying"), comment='endpoint 名称'))
    rpd_limit: int = Field(sa_column=Column('rpd_limit', Integer, nullable=False, server_default=text("'-1'::integer"), comment='周期内请求数限制-请求次数'))
    rpd_duration: int = Field(sa_column=Column('rpd_duration', Integer, nullable=False, server_default=text('60'), comment='周期内请求数限制-时间周期,单位:秒'))
    tpd_limit: int = Field(sa_column=Column('tpd_limit', Integer, nullable=False, server_default=text("'-1'::integer"), comment='周期内 token 数限制 - token 数'))
    tpd_duration: int = Field(sa_column=Column('tpd_duration', Integer, nullable=False, server_default=text('60'), comment='周期内 token 数限制 - 时间周期,单位:秒'))
    ifr_limit: int = Field(sa_column=Column('ifr_limit', Integer, nullable=False, server_default=text("'-1'::integer"), comment='并发请求数(in-flight request)限制'))
    create_at: datetime.datetime = Field(sa_column=Column('create_at', DateTime(True), nullable=False, server_default=text('now()'), comment='创建时间'))
    update_at: datetime.datetime = Field(sa_column=Column('update_at', DateTime(True), nullable=False, server_default=text('now()'), comment='更新时间'))


class LetsgenProviderCredential(SQLModel, table=True):
    __tablename__ = 'letsgen_provider_credential'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='letsgen_provider_credential_pkey'),
        UniqueConstraint('provider_name', 'credential_name', name='uq_letsgen_provider_credential'),
        {'comment': '接入点凭证表'}
    )

    id: int = Field(sa_column=Column('id', BigInteger, primary_key=True, comment='主键'))
    provider_name: str = Field(sa_column=Column('provider_name', String(50), nullable=False, server_default=text("''::character varying"), comment='接入厂商名'))
    credential_name: str = Field(sa_column=Column('credential_name', String(50), nullable=False, server_default=text("''::character varying"), comment='凭证名称'))
    credential_type: str = Field(sa_column=Column('credential_type', String(20), nullable=False, server_default=text("''::character varying"), comment='凭证类型: api_key, credential_file'))
    credential_value: str = Field(sa_column=Column('credential_value', Text, nullable=False, server_default=text("''::text"), comment='凭证值,加密的值'))
    credential_status: str = Field(sa_column=Column('credential_status', String(10), nullable=False, server_default=text("''::character varying"), comment='凭证状态: ok, disabled'))
    expire_at: datetime.datetime = Field(sa_column=Column('expire_at', DateTime(True), nullable=False, server_default=text("'10000-01-01 07:59:59+08'::timestamp with time zone"), comment='凭证过期时间'))
    create_user: str = Field(sa_column=Column('create_user', String(50), nullable=False, server_default=text("''::character varying"), comment='创建者用户名'))
    note: str = Field(sa_column=Column('note', Text, nullable=False, server_default=text("''::text"), comment='凭证备注'))
    create_at: datetime.datetime = Field(sa_column=Column('create_at', DateTime(True), nullable=False, server_default=text('now()')))
    update_at: datetime.datetime = Field(sa_column=Column('update_at', DateTime(True), nullable=False, server_default=text('now()')))


class LetsgenProviderEndpoint(SQLModel, table=True):
    __tablename__ = 'letsgen_provider_endpoint'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='letsgen_provider_endpoint_pkey'),
        UniqueConstraint('provider_name', 'endpoint_name', name='uq_letsgen_provider_endpoint'),
        {'comment': '厂商接入点表'}
    )

    id: int = Field(sa_column=Column('id', BigInteger, primary_key=True, comment='主键'))
    provider_name: str = Field(sa_column=Column('provider_name', String(50), nullable=False, server_default=text("''::character varying"), comment='接入厂商名'))
    endpoint_name: str = Field(sa_column=Column('endpoint_name', String(50), nullable=False, server_default=text("''::character varying"), comment='endpoint 名称'))
    credential_name1: str = Field(sa_column=Column('credential_name1', String(50), nullable=False, server_default=text("''::character varying"), comment='接入点使用的凭证名称1'))
    credential_name2: str = Field(sa_column=Column('credential_name2', String(50), nullable=False, server_default=text("''::character varying"), comment='接入点使用的凭证名称2'))
    endpoint_status: str = Field(sa_column=Column('endpoint_status', String(10), nullable=False, server_default=text("''::character varying"), comment='endpoint 状态: ok, down'))
    endpoint_baseurl: str = Field(sa_column=Column('endpoint_baseurl', String(1024), nullable=False, server_default=text("''::character varying"), comment='endpoint 基础路径'))
    endpoint_region: str = Field(sa_column=Column('endpoint_region', String(50), nullable=False, server_default=text("''::character varying"), comment='endpoint 区域代号'))
    endpoint_proxies: str = Field(sa_column=Column('endpoint_proxies', Text, nullable=False, server_default=text("''::text"), comment='endpoint 使用的代理(多个)'))
    api_format: str = Field(sa_column=Column('api_format', String(50), nullable=False, server_default=text("''::character varying"), comment='接口格式'))
    endpoint_path_info: str = Field(sa_column=Column('endpoint_path_info', Text, nullable=False, server_default=text("''::text"), comment='endpoint path信息. 支持哪些路径,健康检查方式等'))
    endpoint_quota: str = Field(sa_column=Column('endpoint_quota', Text, nullable=False, server_default=text("''::text"), comment='endpoint 容量. rpm/tpm/ifr'))
    note: str = Field(sa_column=Column('note', Text, nullable=False, server_default=text("''::text"), comment='接入点备注'))
    create_at: datetime.datetime = Field(sa_column=Column('create_at', DateTime(True), nullable=False, server_default=text('now()'), comment='创建时间'))
    update_at: datetime.datetime = Field(sa_column=Column('update_at', DateTime(True), nullable=False, server_default=text('now()'), comment='更新时间'))


class LetsgenUser(SQLModel, table=True):
    __tablename__ = 'letsgen_user'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='letsgen_user_pkey'),
        UniqueConstraint('user_name', name='letsgen_user_user_name_key'),
        Index('idx_letsgen_user_create_at', 'create_at'),
        Index('idx_letsgen_user_email', 'user_email'),
        Index('idx_letsgen_user_phone', 'user_phone'),
        Index('idx_letsgen_user_update_at', 'update_at'),
        {'comment': 'UI登录用户表'}
    )

    id: int = Field(sa_column=Column('id', BigInteger, primary_key=True, comment='主键'))
    user_name: str = Field(sa_column=Column('user_name', String(50), nullable=False, server_default=text("''::character varying"), comment='用户名'))
    user_email: str = Field(sa_column=Column('user_email', String(100), nullable=False, server_default=text("''::character varying"), comment='用户邮箱'))
    user_password: str = Field(sa_column=Column('user_password', String(100), nullable=False, server_default=text("''::character varying"), comment='用户密码'))
    user_phone: str = Field(sa_column=Column('user_phone', String(20), nullable=False, server_default=text("''::character varying"), comment='用户手机号'))
    ui_role: str = Field(sa_column=Column('ui_role', String(10), nullable=False, server_default=text("''::character varying"), comment='UI角色:admin,normal'))
    user_status: str = Field(sa_column=Column('user_status', String(10), nullable=False, server_default=text("''::character varying"), comment='用户状态:ok,disabled'))
    note: str = Field(sa_column=Column('note', Text, nullable=False, server_default=text("''::text"), comment='账号备注'))
    create_at: datetime.datetime = Field(sa_column=Column('create_at', DateTime(True), nullable=False, server_default=text('now()'), comment='创建时间'))
    update_at: datetime.datetime = Field(sa_column=Column('update_at', DateTime(True), nullable=False, server_default=text('now()'), comment='更新时间'))


class LetsgenUserAccountRlt(SQLModel, table=True):
    __tablename__ = 'letsgen_user_account_rlt'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='letsgen_user_account_rlt_pkey'),
        UniqueConstraint('user_name', 'account_name', name='uq_letsgen_user_account_rlt'),
        Index('idx_letsgen_user_account_rlt_create_at', 'create_at'),
        Index('idx_letsgen_user_account_rlt_update_at', 'update_at'),
        {'comment': '用户-计费账号关系表'}
    )

    id: int = Field(sa_column=Column('id', BigInteger, primary_key=True, comment='主键'))
    user_name: str = Field(sa_column=Column('user_name', String(50), nullable=False, comment='用户名'))
    account_name: str = Field(sa_column=Column('account_name', String(50), nullable=False, comment='计费账号名'))
    role: str = Field(sa_column=Column('role', String(10), nullable=False, server_default=text("''::character varying"), comment='用户在计费账号下的角色:admin,normal'))
    create_at: datetime.datetime = Field(sa_column=Column('create_at', DateTime(True), nullable=False, server_default=text('now()'), comment='创建时间'))
    update_at: datetime.datetime = Field(sa_column=Column('update_at', DateTime(True), nullable=False, server_default=text('now()'), comment='更新时间'))


class LetsgenWallet(SQLModel, table=True):
    __tablename__ = 'letsgen_wallet'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='letsgen_wallet_pkey'),
        UniqueConstraint('account_name', 'currency_type', name='uq_letsgen_wallet'),
        {'comment': '计费账号钱包表'}
    )

    id: int = Field(sa_column=Column('id', BigInteger, primary_key=True, comment='主键'))
    account_name: str = Field(sa_column=Column('account_name', String(50), nullable=False, comment='计费账号名'))
    currency_type: str = Field(sa_column=Column('currency_type', String(20), nullable=False, server_default=text("''::character varying"), comment='币种类型:USD,CNY,EUR等'))
    cur_balance: decimal.Decimal = Field(sa_column=Column('cur_balance', Numeric(20, 12), nullable=False, server_default=text('0.0'), comment='当前余额'))
    summary_charge: decimal.Decimal = Field(sa_column=Column('summary_charge', Numeric(20, 12), nullable=False, server_default=text('0.0'), comment='累计充值金额'))
    wallet_status: str = Field(sa_column=Column('wallet_status', String(10), nullable=False, server_default=text("''::character varying"), comment='钱包状态:ok,disabled'))
    note: str = Field(sa_column=Column('note', Text, nullable=False, server_default=text("''::text"), comment='钱包备注'))
    create_at: datetime.datetime = Field(sa_column=Column('create_at', DateTime(True), nullable=False, server_default=text('now()'), comment='创建时间'))
    update_at: datetime.datetime = Field(sa_column=Column('update_at', DateTime(True), nullable=False, server_default=text('now()'), comment='更新时间'))
