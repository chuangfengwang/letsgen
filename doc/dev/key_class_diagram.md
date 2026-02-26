
# 关键对象之间的关系

### 普通用户关注

```mermaid
classDiagram
    direction LR

    class User {
    }

    class Account {
    }

    class ApiKey {
    }

    class Wallet {
        一个 Wallet 对应一个计费币种
    }

    class Model {
    }

%% 多对多关系
    User "N" -- "N" Account: "操作"
%% 一对多关系
    Account "1" -- "N" ApiKey: "拥有"
    Account "1" -- "N" Wallet: "拥有"
%% 多对多关系
    Account "N" -- "N" Model: "使用"
```


### 普通管理员关注

```mermaid
classDiagram
    direction LR

    class User {
    }

    class AccountGroup {
    }
    
    class Budget {
    }
    
    Account "N" -- "1" AccountGroup: "属于"
    User "N" -- "N" AccountGroup: "管理"
    Budget "N" -- "N" AccountGroup: "分配预算"
    User "N" -- "N" Budget: "管理预算"
```

### 系统管理员关注

```mermaid
classDiagram
    direction LR
    
    class Model{
    }
    
    class ProviderEndpoint{
    }
    
    class ProviderCredential{
    }
    
    Model "N" -- "N" ProviderEndpoint: "接入"
    ProviderEndpoint "N" -- "N" ProviderCredential: "使用凭证"
```

# 用户角色

- normal: 普通用户, 创建账户, 创建apikey, 使用模型的权限(api/UI), 为账号充值, 为账号申请模型使用权限
- secure: 安全审计, 配置和修改账户安全策略, 审计用户操作日志
- financial: 财务审计, 创建预算, 审批账户组申请的预算, 审计预算使用情况
- group_admin: 账户组管理员, 管理账户组内的账户, 申请预算, 审批账户充值
- admin: 管理员, 所有权限
