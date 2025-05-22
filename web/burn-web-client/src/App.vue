<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>


<template>
  <div class="container" id="main">
    <header>
      <a href="/">
        <img src="./assets/flame.png" />
      </a>
    </header>
    <div id="content">
      <RouterView />      
      <footer>
        <a href="/about">about</a>&nbsp;
        <a href="https://github.com/Tethik/burn-after-reading">github</a>
      </footer>
    </div>
  </div>
</template>

<style scoped>
header {
  text-align: center;
}

footer {
  text-align: right;
}

#main {
  margin-top: 35px;
}

#content {
  padding: 40px;
  border: 1px solid #95a5a6;
  background-color: #ececec;
  box-shadow: 4px 4px #95a5a6;
  margin-bottom: 50px;
}
</style>
