<script>
import {map} from 'lodash'
import {getAdmitCsvExportColumns} from '@/berkeley'

export default {
  name: 'Berkeley',
  methods: {
    getCsvExportColumns: domain => domain === 'default' ? this.getDefaultCsvExportColumns() : getAdmitCsvExportColumns(),
    getCsvExportColumnsSelected: domain => domain === 'default' ? ['first_name', 'last_name', 'sid', 'email', 'phone'] : map(this.getCsvExportColumns(), 'value')
  }
}
</script>
