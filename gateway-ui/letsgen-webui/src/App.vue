<script setup lang="ts">
import { ElConfigProvider } from 'element-plus/es'
</script>

<template>
  <ElConfigProvider :size="'small'" :z-index="3000">
    <div>
      <router-link to="/">首页</router-link> |
      <router-link to="/firstAdminRegister">注册</router-link> |
      <router-link to="/about">关于</router-link>
    </div>
    <router-view></router-view>
  </ElConfigProvider>
</template>

<style scoped></style>
