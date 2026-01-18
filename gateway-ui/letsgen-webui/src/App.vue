<script setup lang="ts">
import { ElConfigProvider } from 'element-plus/es'
</script>

<template>
  <div class="edge-gradient-precise">
    <div class="left-[5%] top-0 h-full w-[90%] bg-white items-center justify-center relative z-10">
      <ElConfigProvider :size="'small'" :z-index="3000">
        <div>
          <router-link to="/">首页</router-link> |
          <router-link to="/loginOrRegister">登录或注册</router-link> |
          <router-link to="/about">关于</router-link> |
          <router-link to="/firstAdminRegister">注册第一个管理员</router-link>
        </div>
        <router-view></router-view>
      </ElConfigProvider>
    </div>
  </div>
</template>

<style scoped>
.edge-gradient-precise {
  background: linear-gradient(90deg,
      /* 左边缘：5%宽度 */
      rgba(139, 92, 246, 1) 0%,
      rgba(139, 92, 246, 0.7) 2%,
      rgba(59, 130, 246, 0.4) 3.5%,
      rgba(255, 255, 255, 0) 5%,

      /* 中间90%白色区域 */
      rgba(255, 255, 255, 1) 5%,
      rgba(255, 255, 255, 1) 95%,

      /* 右边缘：5%宽度（对称） */
      rgba(255, 255, 255, 0) 95%,
      rgba(59, 130, 246, 0.4) 96.5%,
      rgba(139, 92, 246, 0.7) 98%,
      rgba(139, 92, 246, 1) 100%);
}
</style>
