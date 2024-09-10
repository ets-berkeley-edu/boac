<template>
  <div
    id="announcer"
    :aria-live="contextStore.screenReaderAlert.politeness"
    class="sr-only"
  >
    {{ contextStore.screenReaderAlert.message }}
  </div>
  <router-view />
  <DismissibleFooterAlert />
</template>

<script setup>
import DismissibleFooterAlert from '@/components/util/DismissibleFooterAlert'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
</script>

<style>
@import "@/assets/styles/global.css";
@import "@/assets/styles/ckeditor-custom.css";
@import 'v-calendar/style.css';
@import "@/assets/styles/vcalendar-custom.css";
</style>
