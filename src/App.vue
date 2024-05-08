<template>
  <router-view />
  <DismissibleFooterAlert />
</template>

<style>
@import "@/assets/styles/global.css";
@import "@/assets/styles/ckeditor-custom.css";
@import "@/assets/styles/vcalendar-custom.css";
</style>

<script setup>
import DismissibleFooterAlert from '@/components/util/DismissibleFooterAlert'
</script>
