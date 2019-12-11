<template>
  <transition name="drawer">
    <div v-show="isOpen" class="drawer">
      <div class="ml-4 mr-4 p-2 row">
        <div class="col-sm pr-2">
          <h3>
            Advisor(s)
          </h3>
          <div>
            <div>
              <strong>College Advisor</strong>
            </div>
            <div>
              Letters & Sci Undeclared UG
            </div>
            <div>
              Paulette Jacobs
            </div>
            <div>
              paulette.jacobs@berkeley.edu
            </div>
          </div>
        </div>
        <div class="col-sm pr-2">
          <h3>
            Contact Information
          </h3>
          <div>
            <div>
              <strong>Other Email (preferred)</strong>
            </div>
            <div>
              paulette.jacobs@berkeley.edu
            </div>
          </div>
          <div>
            <div>
              <strong>Mobile Phone (preferred)</strong>
            </div>
            <div>
              (510) 555-1212
            </div>
          </div>
          <div>
            <div>
              <strong>Home/Permanent Phone</strong>
            </div>
            <div>
              (510) 555-1234
            </div>
          </div>
          <h3>
            Additional Information
          </h3>
          <div>
            <div>
              Transfer
            </div>
            <div>
              Entered Fall 2017
            </div>
            <div>
              Women's Sportsball
            </div>
            <div class="no-wrap mt-1">
              <a
                id="link-to-calcentral"
                :href="`https://calcentral.berkeley.edu/user/overview/${student.uid}`"
                target="_blank"
                aria-label="Open CalCentral in new window">Student profile in CalCentral <font-awesome icon="external-link-alt" class="pr-1" /></a>
            </div>
          </div>
        </div>
        <div class="col-sm pr-2">
          <h3>
            Intended Major
          </h3>
          <div>
            <div>
              <strong>Comparative Literature BA</strong>
            </div>
            <div>
              Undergraduate Letters & Science
            </div>
          </div>
          <h3>
            Discontinued Majors
          </h3>
          <div>
            <div>
              <strong>Non-UC Campus Visitor L&S UG</strong>
            </div>
            <div>
              Undergrad Non-Degree/NonFinAid
            </div>
            <div>
              Discontinued on 2/15/2018
            </div>
          </div>
          <div>
            <div>
              <strong>Non-UC Campus Visitor EVCP UG</strong>
            </div>
            <div>
              Undergrad Non-Degree/NonFinAid
            </div>
            <div>
              Discontinued on 2/15/2018
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'StudentPersonalDetails',
  props: {
    isOpen: {
      required: false,
      type: Boolean
    },
    student: {
      required: false,
      type: Object
    }
  }
}
</script>

<style scoped>
.drawer {
  background-color: #f5fbff;
}
.drawer-enter-active {
   -webkit-transition-duration: 0.3s;
   transition-duration: 0.3s;
   -webkit-transition-timing-function: ease-in;
   transition-timing-function: ease-in;
}
.drawer-leave-active {
   -webkit-transition-duration: 0.3s;
   transition-duration: 0.5s;
   -webkit-transition-timing-function: cubic-bezier(0, 1, 0.5, 1);
   transition-timing-function: cubic-bezier(0, 1, 0.5, 1);
}
.drawer-enter-to, .drawer-leave {
  max-height: 280px;
  overflow: hidden;
}
.drawer-enter, .drawer-leave-to {
  overflow: hidden;
  max-height: 0;
}
</style>
