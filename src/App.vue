<template>
  <div id="app" class="fill-viewport">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
};
</script>

<style>
.fill-viewport {
  height: 100%;
  font-size: 14px;
}
.btn-link:active,
.btn-link:focus,
.btn-link:focus-within,
.btn-link:hover {
  text-decoration: none !important;
}
</style>
