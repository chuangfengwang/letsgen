<template>
    <h1>注册第一个管理员</h1>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" style="max-width: 600px">
        <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" @keyup.enter="onSubmit" />
        </el-form-item>
        <el-form-item label="设置密码" prop="password">
            <el-input v-model="form.password" show-password @keyup.enter="onSubmit"/>
        </el-form-item>
        <el-form-item label="重复密码" prop="confirmPassword">
            <el-input v-model="form.confirmPassword" show-password @keyup.enter="onSubmit"/>
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="onSubmit">Create</el-button>
            <el-button @click="onCancel">Cancel</el-button>
        </el-form-item>
    </el-form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'

const formRef = ref()

const form = reactive({
    username: '',
    password: '',
    confirmPassword: ''
})

// 自定义验证函数：验证确认密码与密码是否一致
const validateConfirmPassword = (rule: any, value: string, callback: any) => {
    if (value === '') {
        callback(new Error('请再次输入密码'))
    } else if (value !== form.password) {
        callback(new Error('两次输入的密码不一致'))
    } else {
        callback()
    }
}

const rules = {
    username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' }
    ],
    confirmPassword: [
        { required: true, validator: validateConfirmPassword, trigger: 'blur' }
    ]
}

const onSubmit = async () => {
    if (!formRef.value) return
    
    try {
        await formRef.value.validate()
        console.log(form)
        // 这里可以添加实际的提交逻辑
    } catch (error) {
        console.log('表单验证失败', error)
    }
}

const onCancel = () => {
    formRef.value?.resetFields()
}
</script>