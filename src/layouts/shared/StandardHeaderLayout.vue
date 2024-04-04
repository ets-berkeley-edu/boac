<template>
  <v-container
    class="my-2 py-0"
    fluid
    @shortkey="() => putFocusNextTick('search-students-input')"
  >
    <v-row no-gutters>
      <v-col align-self="center" cols="auto" md="4">
        <div class="py-2">
          <HeaderBranding />
        </div>
      </v-col>
      <v-col>
        <AdvancedSearch />
      </v-col>
      <v-col align-self="center" cols="auto" sm>
        <HeaderMenu class="float-right" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import AdvancedSearch from '@/components/search/AdvancedSearch'
import {putFocusNextTick} from '@/lib/utils'
</script>

<script>
import HeaderBranding from '@/layouts/shared/HeaderBranding'
import HeaderMenu from '@/components/header/HeaderMenu'

export default {
  name: 'StandardHeaderLayout',
  components: {HeaderBranding, HeaderMenu}
}
</script>
