<template>
  <div class="align-center d-flex">
    <div class="quick-links-label">
      Quick links:
    </div>
    <div>
      <v-btn
        id="quick-link-ce3-advisors"
        class="font-size-16 px-2"
        color="primary"
        :disabled="disabled"
        text="CE3"
        variant="text"
        @click="onClickQuickLink('ZCEEE', 'quick-link-ce3-advisors')"
      />
    </div>
    <div>
      |
    </div>
    <div>
      <v-btn
        id="quick-link-coe-advisors"
        class="font-size-16 px-2"
        color="primary"
        :disabled="disabled"
        exact
        text="COENG Advisors"
        variant="text"
        @click="onClickQuickLink('COENG', 'quick-link-coe-advisors')"
      />
    </div>
    <div>
      |
    </div>
    <div>
      <v-btn
        id="quick-link-qcadv-advisors"
        class="font-size-16 px-2"
        color="primary"
        :disabled="disabled"
        exact
        text="L&amp;S Advisors"
        variant="text"
        @click="onClickQuickLink('QCADV', 'quick-link-qcadv-advisors')"
      />
    </div>
    <div>
      |
    </div>
    <div>
      <v-btn
        id="quick-link-peer-advising"
        class="font-size-16 px-2"
        color="primary"
        :disabled="disabled"
        exact
        text="Peer Advising"
        variant="text"
        @click="onClickPeerAdvisingQuickLink"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  disabled: {
    required: false,
    type: Boolean
  },
  onClickPeerAdvisingQuickLink: {
    required: true,
    type: Function
  },
  onClickQuickLink: {
    required: true,
    type: Function
  }
})
</script>

<style scoped>
.quick-links-label {
  font-size: 18px;
  font-weight: 600;
  padding-bottom: 1px;
}
</style>
