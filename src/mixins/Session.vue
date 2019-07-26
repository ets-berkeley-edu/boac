<script>
import { ping } from '@/api/config';

export default {
  name: 'Session',
  created() {
    // Keep session alive with periodic requests
    if (this.pingFrequency) {
      setInterval(ping, this.pingFrequency);
    }
  }
};
</script>