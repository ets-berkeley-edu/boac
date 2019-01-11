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
.b-dd-item-override {
  color: #212529 !important;
}
.b-dd-primary-override {
  background-color: #337ab7;
  border-color: #2e6da4;
  border-top-right-radius: 0.3em !important;
  border-bottom-right-radius: 0.3em !important;
  margin-left: 5px !important;
}
.b-dd-primary-override:active,
.b-dd-primary-override:focus,
.b-dd-primary-override:hover {
  background-color: #286090;
  border-color: #204d74;
}
.btn-link:active,
.btn-link:focus,
.btn-link:focus-within,
.btn-link:hover {
  text-decoration: none !important;
}
.fill-viewport {
  height: 100%;
  font-size: 14px;
}
h1 {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 10px 0;
}
</style>
