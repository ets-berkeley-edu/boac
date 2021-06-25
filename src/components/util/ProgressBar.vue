<template>
  <div id="progress-bar">
    <div class="progress-bar-container">
      <div
        class="progress-bar-display"
        role="progressbar"
        aria-valuemin="0"
        aria-valuemax="100"
        :aria-valuenow="percentComplete"
      >
        <div class="progress-bar-status">{{ percentComplete }}% Complete</div>
        <div class="progress-bar-value" :style="{ width: percentComplete + '%' }"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProgressBar',
  props: {
    percentComplete: {
      type: Number,
      default: 0
    }
  }
}
</script>

<style scoped>
.progress-bar-container {
  margin: 35px auto;
  width: 75%;
}
.progress-bar-display {
  border: 1px solid grey;
  border-radius: 3px;
  height: 30px;
  overflow: hidden;
  position: relative;
}
.progress-bar-status {
  font-size: 14px;
  font-weight: bold;
  left: 50%;
  line-height: 28px;
  margin-left: -75px;
  position: absolute;
  text-align: center;
  width: 150px;
}
.progress-bar-value {
  background-image: linear-gradient(to bottom, #3883c5, #296396);
  height: 100%;
}
</style>
