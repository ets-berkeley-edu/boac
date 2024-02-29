<template>
  <div class="border-top pt-2">
    <div class="py-1">
      <router-link
        v-if="parentTemplateUpdatedAt"
        id="degree-template-source"
        target="_blank"
        :to="`/degree/${parentTemplateId}`"
      >
        <font-awesome icon="external-link-alt" />
        Created from template <span class="sr-only"> (will open new browser tab)</span>
      </router-link>
    </div>
    <div class="pb-1">
      <b-btn
        class="px-0"
        :disabled="!disableButtons"
        variant="link"
        @click="setDisableButtons(false)"
      >
        <font-awesome
          :class="disableButtons ? 'text-primary' : 'text-black-50'"
          icon="play-circle"
        />
        Force buttons to enable
      </b-btn>
    </div>
    <div class="align-items-center d-flex">
      <div class="pr-1">
        <font-awesome icon="bug" />
      </div>
      <div class="pr-2">
        Debug
      </div>
      [<b-button class="m-0 p-0" variant="link" @click="showDebug = !showDebug">{{ showDebug ? 'hide' : 'show' }}</b-button>]
    </div>
    <transition name="drawer">
      <pre v-if="showDebug">{{ degreeEditSessionToString }}</pre>
    </transition>
  </div>
</template>

<script>
import DegreeEditSession from '@/mixins/DegreeEditSession'

export default {
  name: 'DebugTemplate',
  mixins: [DegreeEditSession],
  data: () => ({
    showDebug: false
  })
}
</script>
