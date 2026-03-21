<template>
  <div>
    <div
      id="announcer"
      :aria-live="contextStore.screenReaderAlert.politeness"
      class="sr-only"
    >
      {{ contextStore.screenReaderAlert.message }}
    </div>
    <router-view :aria-hidden="contextStore.isModalOpen" :inert="contextStore.isModalOpen" />
    <DismissibleFooterAlert :aria-hidden="contextStore.isModalOpen" :inert="contextStore.isModalOpen" />
  </div>
</template>

<script setup>
import DismissibleFooterAlert from '@/components/util/DismissibleFooterAlert'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
</script>

<style>
@import 'v-calendar/style.css';
@import "@/assets/styles/vcalendar-custom.css";
@import 'ckeditor5/ckeditor5.css';
@import "@/assets/styles/ckeditor-custom.css";
@import "@/assets/styles/global.css";
@import "@/assets/styles/focus.scss";
</style>
