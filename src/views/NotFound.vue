<template>
  <div class="page-not-found-background-image"></div>
</template>

<script>
export default {
  name: 'NotFound'
};
</script>

<style scoped>
.page-not-found-background-image {
  background: url('~@/assets/404_lost_in_the_clouds.jpg') no-repeat center
    center;
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
  height: 100%;
  width: 100%;
}
</style>
