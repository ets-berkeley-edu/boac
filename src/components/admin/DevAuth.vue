<template>
  <div class="d-flex dev-auth px-7">
    <v-text-field
      id="dev-auth-uid"
      v-model="uid"
      aria-label="Input UID of an authorized user"
      aria-required="true"
      class="form-input"
      :disabled="isLoggingIn"
      hide-details
      placeholder="UID"
      @keydown.enter="logIn"
      @update:model-value="() => reportError(null)"
    />
    <v-text-field
      id="dev-auth-password"
      v-model="password"
      :aria-invalid="!!password"
      aria-label="Password"
      aria-required="true"
      class="form-input"
      :disabled="isLoggingIn"
      hide-details
      placeholder="Password"
      type="password"
      @keydown.enter="logIn"
      @update:model-value="() => reportError(null)"
    />
    <v-btn
      id="dev-auth-submit"
      class="btn-dev-auth"
      color="primary"
      :disabled="isLoggingIn"
      elevation="0"
      text="DevAuth!"
    />
  </div>
</template>

<script setup>
import router from '@/router'
import {devAuthLogIn} from '@/api/auth'
import {get, trim} from 'lodash'
import {onMounted, ref} from 'vue'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  reportError: {
    required: true,
    type: Function
  }
})

const contextStore = useContextStore()
const isLoggingIn = ref(false)
const uid = ref('')
const password = ref('')

onMounted(() => putFocusNextTick('dev-auth-uid'))

const logIn = () => {
  uid.value = trim(uid.value)
  password.value = trim(password.value)
  if (uid.value && password.value) {
    isLoggingIn.value = true
    devAuthLogIn(uid.value, password.value).then(
      () => {
        if (contextStore.currentUser.isAuthenticated) {
          const redirect = get(router, 'currentRoute.query.redirect')
          router.push({path: redirect || '/home'}).then(() => {
            isLoggingIn.value = false
          })
        } else {
          props.reportError('Sorry, user is not authorized to use BOA.')
          isLoggingIn.value = false
        }
      },
      error => {
        props.reportError(error)
      }
    )
  } else if (uid.value) {
    props.reportError('Password required')
    putFocusNextTick('dev-auth-password')
  } else {
    props.reportError('Both UID and password are required')
    putFocusNextTick('dev-auth-uid')
  }
}
</script>

<style lang="scss" scoped>
.btn-dev-auth {
  height: 28px;
  padding: 0 5px;
  text-transform: capitalize;
}
.dev-auth {
  justify-content: center;
  padding-top: 10px;
  white-space: nowrap;
}
.form-input {
  padding-right: 5px;
}
</style>

<style lang="scss">
.dev-auth {
  .form-input {
    input {
      height: 28px;
      min-height: unset;
      padding: 8px;
    }
  }
}
</style>
