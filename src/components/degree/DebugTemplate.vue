<template>
  <div class="border-top pt-2">
    <transition name="drawer">
      <div v-if="disableButtons" class="align-items-center d-flex pb-2">
        <div class="pr-1">
          <font-awesome icon="play-circle" />
        </div>
        <div>
          <b-btn
            class="px-0"
            variant="link"
            @click="setDisableButtons(false)"
          >
            Force buttons to enable
          </b-btn>
        </div>
      </div>
    </transition>
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
