<script>
import { getDropInAppointmentWaitlist } from '@/api/appointments';

export default {
  name: 'DropInWaitlistContainer',
  methods: {
    loadDropInWaitlist() {
      getDropInAppointmentWaitlist(this.deptCode, this.includeResolvedAppointments).then(waitlist => {
        let announceLoad = false;
        let announceUpdate = false;
        if (!this.isEqual(waitlist, this.waitlist)) {
          if (this.waitlist) {
            announceUpdate = true;
          } else {
            announceLoad = true;
          }
          this.waitlist = waitlist;
        }
        if (announceLoad) {
          this.loaded('Appointment waitlist');
        }
        if (announceUpdate) {
          this.alertScreenReader('The appointment waitlist has been updated');
        }
      });
    }
  }
}
</script>
