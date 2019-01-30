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
.avatar {
  background-image: url('~@/assets/avatar-50.png');
  background-size: cover;
  border: 5px solid #ccc;
  border-radius: 30px;
  height: 60px;
  object-fit: cover;
  width: 60px;
}
.b-dd-item-override {
  color: #212529 !important;
}
.b-dd-override {
  background-color: #337ab7;
  border-color: #2e6da4;
  border-top-right-radius: 0.3em !important;
  border-bottom-right-radius: 0.3em !important;
  margin-left: 5px !important;
}
.b-dd-override:active,
.b-dd-override:focus,
.b-dd-override:hover {
  background-color: #286090;
  border-color: #204d74;
}
.b-dd-narrow {
  height: 35px !important;
  margin-left: 0 !important;
  min-width: 160px !important;
  width: 160px !important;
}
.btn-primary-color-override {
  background-color: #337ab7 !important;
  border-color: #2e6da4 !important;
}
.btn-primary-color-override:hover,
.btn-primary-color-override:focus,
.btn-primary-color-override:active {
  background-color: #286090 !important;
  border-color: #204d74 !important;
}
.btn-link:active,
.btn-link:focus,
.btn-link:focus-within,
.btn-link:hover {
  text-decoration: none !important;
}
.boac-exclamation {
  color: #f0ad4e;
}
.demo-mode-blur {
  color: transparent !important;
  text-shadow: 0 0 15px rgba(0, 0, 0, 0.5) !important;
}
.demo-mode-blur:hover {
  color: transparent !important;
  text-shadow: 0 0 20px rgba(0, 0, 0, 0.5) !important;
}
.faint-text {
  color: grey;
}
.fill-viewport {
  height: 100%;
  font-size: 14px;
}
.flex-container {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}
.flex-row {
  display: flex;
  flex-direction: row;
}
.form-control {
  height: 38px;
  padding: 8px 12px;
}
.full-width {
  width: 100%;
}
.has-error {
  color: #cf1715;
}
.img-blur {
  -webkit-filter: blur(10px);
  filter: blur(10px);
}
.no-wrap {
  white-space: nowrap;
}
.page-section-header {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
  margin-top: 20px;
}
.page-section-header-sub {
  font-size: 18px;
  font-weight: bold;
}
.panel {
  -webkit-box-shadow: none;
  box-shadow: 0;
}
.red-flag-status {
  color: #d0021b;
  font-weight: bold;
}
.red-flag-small {
  color: #d0021b;
  font-size: 12px;
  font-weight: bold;
}
.table-full-width {
  margin: 10px 0;
  table-layout: fixed;
  width: 100%;
}

html,
body {
  height: 100%;
}
h1 {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 10px 0;
}
select[data-value=''],
select option[value=''] {
  color: #999;
}
select.form-control {
  padding-left: 6px;
  width: 150px;
}

#content {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
#content a,
#content .btn-link {
  color: #337ab7;
}
#content .btn-link-close {
  border: 0;
  color: #000;
  float: right;
  font-size: 21px;
  font-weight: 700;
  line-height: 1;
  padding: 0;
  opacity: 0.2;
  text-shadow: 0 1px 0 #fff;
}
#content h1:focus {
  outline: none;
}
#content .list-group-item-info {
  color: #31708f;
  background-color: #d9edf7;
}
#content .nav-pills .nav-link.active,
#content .nav-pills .show > .nav-link {
  background-color: #337ab7;
  color: #fff;
}
#content .tab-button {
  background-color: #6bd;
  border: 1px solid transparent;
  color: #fff;
  font-size: 14px;
  opacity: 1;
}
#content .tab-button:hover {
  color: #cef;
}
#content .tab-button:disabled {
  cursor: not-allowed;
}
#content .tab-btn-group {
  padding: 0 0 5px 0;
}
#content .tab-button-selected {
  background-color: #49b;
}
#content .tab-button-selected:active,
#content .tab-button-selected:focus {
  color: #fff;
  outline: none !important;
}
#content .toggle-btn-link {
  font-size: 14px;
}
</style>
