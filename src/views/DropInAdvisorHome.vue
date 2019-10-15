<template>
  <div class="ml-3 mt-3">
    <h1 class="sr-only">Welcome to BOA</h1>
    <Spinner />
    <div v-if="!loading" class="home-content">
      <h1>Drop-in Advisor Homepage</h1>
      <div>
        Hello World
      </div>
    </div>
  </div>
</template>

<script>
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';

export default {
  name: 'DropInAdvisorHome',
  components: {Spinner},
  mixins: [Loading],
  mounted() {
    this.loaded();
  }
}
</script>
