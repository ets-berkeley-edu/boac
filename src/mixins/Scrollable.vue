<script>
import VueScrollTo from 'vue-scrollto';

export default {
  name: 'Scrollable',
  methods: {
    scrollTo: anchor => {
      VueScrollTo.scrollTo(anchor, 600);
    }
  }
};
</script>
