<script>
import VueScrollTo from 'vue-scrollto';

export default {
  name: 'Scrollable',
  methods: {
    scrollTo: anchor => VueScrollTo.scrollTo(anchor, 400),
    scrollToTop: () => VueScrollTo.scrollTo('#app', 400)
  }
};
</script>
