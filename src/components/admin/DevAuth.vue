<template>
  <form @submit.prevent="logIn">
    <div class="d-flex dev-auth px-7">
      <v-text-field
        id="dev-auth-uid"
        v-model="uid"
        aria-label="Input UID of an authorized user"
        aria-required="true"
        class="form-input"
        density="compact"
        hide-details
        placeholder="UID"
        variant="outlined"
        @update:model-value="() => reportError(null)"
      />
      <v-text-field
        id="dev-auth-password"
        v-model="password"
        :aria-invalid="!!password"
        aria-label="Password"
        aria-required="true"
        class="form-input"
        density="compact"
        :disabled="isLoggingIn"
        hide-details
        placeholder="Password"
        type="password"
        variant="outlined"
        @update:model-value="() => reportError(null)"
      />
      <v-btn
        id="dev-auth-submit"
        class="btn-dev-auth"
        color="primary"
        :disabled="isLoggingIn"
        elevation="0"
        type="submit"
      >
        DevAuth!
      </v-btn>
    </div>
  </form>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {devAuthLogIn} from '@/api/auth'
import {noop} from 'lodash'

export default {
  name: 'DevAuth',
  mixins: [Context, Util],
  props: {
    reportError: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    isLoggingIn: false,
    uid: null,
    password: null
  }),
  created() {
    this.putFocusNextTick('dev-auth-uid')
  },
  methods: {
    logIn() {
      let uid = this._trim(this.uid)
      let password = this._trim(this.password)
      if (uid && password) {
        this.isLoggingIn = true
        devAuthLogIn(uid, password).then(
          () => {
            if (this.currentUser.isAuthenticated) {
              const redirect = this._get(this.$router, 'currentRoute.query.redirect')
              this.$router.push({path: redirect || '/home'}, noop)
            } else {
              this.reportError('Sorry, user is not authorized to use BOA.')
            }
          },
          error => {
            this.reportError(error)
          }
        ).finally(() => {
          this.isLoggingIn = false
        })
      } else if (uid) {
        this.reportError('Password required')
        this.putFocusNextTick('dev-auth-password')
      } else {
        this.reportError('Both UID and password are required')
        this.putFocusNextTick('dev-auth-uid')
      }
    }
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
