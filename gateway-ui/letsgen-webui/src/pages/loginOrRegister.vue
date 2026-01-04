<template>
    <div class="auth-container">
        <el-card class="auth-card">
            <template #header>
                <h2 class="auth-title">Letsgen Gateway: 企业级大模型网关</h2>
            </template>

            <el-tabs v-model="activeTab" stretch>
                <el-tab-pane label="登录" name="login">
                    <el-form :model="loginForm" :rules="rules" ref="loginRef" label-position="top">
                        <el-form-item label="账号" prop="username">
                            <el-input v-model="loginForm.username" placeholder="请输入用户名"
                                @compositionstart="isComposing = true" @compositionend="isComposing = false"
                                @keyup.enter="handleLoginEnter" />
                        </el-form-item>
                        <el-form-item label="密码" prop="password">
                            <el-input v-model="loginForm.password" type="password" show-password placeholder="请输入密码"
                                @keyup.enter="handleLoginEnter" />
                        </el-form-item>
                        <el-button type="primary" class="submit-btn" @click="handleLogin">登录</el-button>
                        <el-button type="info" class="cancel-btn" @click="loginCancel">取消</el-button>
                    </el-form>
                </el-tab-pane>

                <el-tab-pane label="注册" name="register">
                    <el-form :model="registerForm" :rules="rules" ref="registerRef" label-position="top">
                        <el-form-item label="账号" prop="username">
                            <el-input v-model="registerForm.username" placeholder="设置用户名" />
                        </el-form-item>
                        <el-form-item label="密码" prop="password">
                            <el-input v-model="registerForm.password" type="password" show-password
                                placeholder="设置密码" />
                        </el-form-item>
                        <el-form-item label="确认密码" prop="confirmPassword">
                            <el-input v-model="registerForm.confirmPassword" type="password" show-password
                                placeholder="请再次输入密码" />
                        </el-form-item>
                        <el-form-item label="电子邮箱" prop="email">
                            <el-input v-model="registerForm.email" placeholder="请输入电子邮箱" />
                        </el-form-item>
                        <el-form-item label="手机号" prop="phone">
                            <el-input v-model="registerForm.phone" placeholder="请输入手机号" />
                        </el-form-item>
                        <el-button type="success" class="submit-btn" @click="handleRegister">注册</el-button>
                        <el-button type="info" class="cancel-btn" @click="registerCancel">取消</el-button>
                    </el-form>
                </el-tab-pane>
            </el-tabs>
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus/es'
import { register } from '../api/nonlogin-request'
import { login } from '../api/nonlogin-request'

// 当前激活的 Tab
const activeTab = ref('login')
const isComposing = ref(false)

// 表单引用
const loginRef = ref()
const registerRef = ref()

// 数据绑定
const loginForm = reactive({ username: '', password: '' })
const registerForm = reactive({ username: '', password: '', confirmPassword: '', email: '', phone: '' })

// 校验逻辑：确认密码是否一致
const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
    if (value === '') {
        callback(new Error('请再次输入密码'))
    } else if (value !== registerForm.password) {
        callback(new Error('两次输入的密码不一致'))
    } else {
        callback()
    }
}

// 校验规则
const rules = {
    username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
    password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码不能少于 6 位', trigger: 'blur' }],
    confirmPassword: [
        { required: true, message: '请再次输入密码', trigger: 'blur' },
        { validator: validateConfirmPassword, trigger: 'blur' }
    ]
}

// 登录提交
const handleLogin = async () => {
    if (!loginRef.value) return

    try {
        await loginRef.value.validate()

        login({
            user_name: loginForm.username,
            password_plain: loginForm.password,
        }).then(res => {
            ElMessage({
                message: '登录成功',
                type: 'success',
                duration: 5000
            })
        })
    } catch (error) {
        // do nothing
    }
}

const handleLoginEnter = () => {
    // 如果正在使用输入法，忽略 Enter 键
    if (isComposing.value) {
        return
    }
    handleLogin()
}

// 取消登录
const loginCancel = () => {
    loginRef.value?.resetFields()
}

// 注册提交
const handleRegister = async () => {
    if (!registerRef.value) return

    // 这里可以添加实际的提交逻辑
    register({
        user_name: registerForm.username,
        password_plain: registerForm.password,
        user_email: registerForm.email || undefined, // 如果为空字符串，发送 undefined
        user_phone: registerForm.phone || undefined, // 如果为空字符串，发送 undefined
    }).then(res => {
        // TODO: 显示成功提示，跳转页面等
        ElMessage({
            message: '注册成功',
            type: 'success',
            duration: 5000
        })
    }).catch(err => {
        // 接口失败, 接口调用会统一拦截并触发痰喘错误信息
    })
}

// 当密码字段改变时，重新验证确认密码字段
watch(
    () => registerForm.password,
    () => {
        if (registerRef.value && registerForm.confirmPassword) {
            registerRef.value.validateField('confirmPassword')
        }
    },
)

const handleRegisterEnter = () => {
    // 如果正在使用输入法，忽略 Enter 键
    if (isComposing.value) {
        return
    }
    handleRegister()
}

// 取消注册
const registerCancel = () => {
    registerRef.value?.resetFields()
}
</script>

<style scoped>
.auth-container {
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #f5f7fa;
}

.auth-card {
    width: 400px;
    border-radius: 8px;
}

.auth-title {
    text-align: center;
    margin: 0;
    color: #409eff;
}

.submit-btn {
    width: 45%;
    margin-top: 10px;
}

.cancel-btn {
    width: 45%;
    margin-top: 10px;
}
</style>