<script>
import VueScrollTo from 'vue-scrollto'

export default {
  name: 'Scrollable',
  methods: {
    scrollTo: anchor => VueScrollTo.scrollTo(anchor, 400),
    scrollToTop: delay => VueScrollTo.scrollTo('#app', (delay || 400))
  }
}
</script>
