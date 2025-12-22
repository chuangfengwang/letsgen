<template>
  <div>
    <h2 @click="add">{{ count }}</h2>
    <input type="text" v-model="title" @keydown.enter="addTodo" />
  </div>
  <ul v-if="todoList.length > 0">
    <li v-for="todo in todoList" :key="todo.title">
      <input type="checkbox" v-model="todo.done" />
      <span :class="{ done: todo.done }">{{ todo.title }}</span>
    </li>
  </ul>
  <p v-else>暂无待办事项</p>
  <button @click="clearTodo">清空</button>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Todo {
  title: string
  done: boolean
}

const count = ref(1)
const title = ref('')
const todoList = ref<Todo[]>([])
const add = () => {
  count.value++
}
const addTodo = () => {
  todoList.value.push({
    title: title.value,
    done: false,
  })
  title.value = ''
}
const clearTodo = () => {
  todoList.value = []
}
</script>

<style scoped>
h2 {
  color: red;
}
.done {
  text-decoration: line-through;
  color: #999;
}
</style>
