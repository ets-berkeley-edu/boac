<template>
  <div id="app">
    <Container>
      <Header/>
      <div class="content">
        <router-view/>
      </div>
      <Footer/>
    </Container>
  </div>
</template>

<script>
import Container from './components/Container.vue';
import Footer from './components/Footer.vue';
import Header from './components/Header.vue';

export default {
  name: 'App',
  components: {
    Header,
    Container,
    Footer
  }
};
</script>

<style src="./boac.css">
</style>
