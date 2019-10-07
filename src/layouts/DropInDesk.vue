<template>
  <div>
    <a
      id="skip-to-content-link"
      href="#content"
      class="sr-only sr-only-focusable"
      tabindex="0">Skip to main content</a>
    <div>
      <HeaderMenu />
    </div>
    <div id="content">
      <div
        v-if="announcement && announcement.isPublished"
        style="display: inline-block"
        class="service-announcement pl-3 pt-3 pr-3 pb-0 w-100">
        <span
          id="service-announcement-banner"
          aria-live="polite"
          role="alert"
          v-html="announcement.text">
        </span>
      </div>
      <div>
        <span
          v-if="srAlert"
          class="sr-only"
          aria-live="polite"
          role="alert">
          {{ srAlert }}
        </span>
        <router-view :key="stripAnchorRef($route.fullPath)"></router-view>
      </div>
    </div>
    <div v-if="!loading">
      <Footer />
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import Footer from '@/components/Footer';
import HeaderMenu from '@/components/HeaderMenu';
import Loading from '@/mixins/Loading';
import Session from '@/mixins/Session';
import Util from '@/mixins/Util';

export default {
  name: 'DropInDesk',
  components: {
    Footer,
    HeaderMenu
  },
  mixins: [Context, Loading, Session, Util]
}
</script>

<style scoped>

</style>
