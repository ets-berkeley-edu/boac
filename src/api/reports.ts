import axios from 'axios';
import utils from '@/api/api-utils';

export function getBoaUsageSummary(deptCode) {
  let url = `${utils.apiBaseUrl()}/api/reports/boa_usage_summary/${deptCode}`;
  return axios.get(url).then(response => response.data, () => null);
}
