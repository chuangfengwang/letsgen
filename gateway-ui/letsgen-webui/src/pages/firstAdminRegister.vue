<template>
  <p class="text-2xl font-bold">创建第一个管理员</p>
  <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" style="max-width: 600px">
    <el-form-item label="用户名" prop="username">
      <el-input v-model="form.username" @compositionstart="isComposing = true" @compositionend="isComposing = false"
        @keyup.enter="handleEnter" />
    </el-form-item>
    <el-form-item label="设置密码" prop="password">
      <el-input v-model="form.password" show-password @compositionstart="isComposing = true"
        @compositionend="isComposing = false" @keyup.enter="handleEnter" />
    </el-form-item>
    <el-form-item label="重复密码" prop="confirmPassword">
      <el-input v-model="form.confirmPassword" show-password @compositionstart="isComposing = true"
        @compositionend="isComposing = false" @keyup.enter="handleEnter" />
    </el-form-item>
    <el-form-item label="电子邮箱">
      <el-input v-model="form.email" @compositionstart="isComposing = true"
        @compositionend="isComposing = false" @keyup.enter="handleEnter" />
    </el-form-item>
    <el-form-item label="手机号">
      <el-input v-model="form.phone" @compositionstart="isComposing = true"
        @compositionend="isComposing = false" @keyup.enter="handleEnter" />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="onSubmit">创建</el-button>
      <el-button @click="onCancel">取消</el-button>
    </el-form-item>
  </el-form>
  <div>
    <p>说明：</p>
    <ol>
      <li>该页面只用于系统初始化时创建第一个管理员</li>
      <li>其他管理员请通过任意一个管理员调整其他普通用户角色来实现</li>
      <li>系统至少保留一个管理员</li>
    </ol>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { registerFirstAdmin } from '../api/nonlogin-request'
import { ElMessage } from 'element-plus/es'

const formRef = ref()
const isComposing = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  email: '',
  phone: '',
})

// 使用 Element Plus 推荐的验证规则写法
const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  confirmPassword: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }],
}

// 当密码字段改变时，重新验证确认密码字段
watch(
  () => form.password,
  () => {
    if (formRef.value && form.confirmPassword) {
      formRef.value.validateField('confirmPassword')
    }
  },
)

const handleEnter = () => {
  // 如果正在使用输入法，忽略 Enter 键
  if (isComposing.value) {
    return
  }
  onSubmit()
}

const onSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    // 这里可以添加实际的提交逻辑
    registerFirstAdmin({
      user_name: form.username,
      password_plain: form.password,
      user_email: form.email || undefined, // 如果为空字符串，发送 undefined
      user_phone: form.phone || undefined, // 如果为空字符串，发送 undefined
    }).then(res => {
      // TODO: 显示成功提示，跳转页面等
      ElMessage({
        message: '注册成功',
        type: 'success',
        duration: 5000
      })
    }).catch(err => {
      // console.error('注册失败:', err)
      // TODO: 显示错误提示（可以使用 Element Plus 的 ElMessage）
      // alert(err.message || '注册失败，请检查输入信息')
      // ElMessage({
      //   message: err.message || '注册失败，请检查输入信息',
      //   type: 'error',
      //   duration: 5000
      // })
    })
  } catch (error) {
    // do nothing
  }
}

const onCancel = () => {
  formRef.value?.resetFields()
}
</script>
