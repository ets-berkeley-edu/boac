<template>
  <div class="flex-row footer-container">
    <div>
      <img src="@/assets/uc-berkeley-logo.svg"/>
    </div>
    <div class="copyright">
      &copy; 2018 The Regents of the University of California
    </div>
  </div>
</template>

<script>
export default {
  name: 'Footer'
};
</script>

<style scoped lang="scss">
.footer-container {
  align-items: flex-end;
  justify-content: space-between;
  padding-bottom: 20px;
}
.copyright {
  display: inline-block;
  white-space: nowrap;
}
</style>
