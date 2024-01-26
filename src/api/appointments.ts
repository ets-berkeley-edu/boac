import axios from 'axios'
import ga from '@/ga'
import utils from '@/api/api-utils'

const $_track = action => ga.appointment(action)

export function markAppointmentRead(appointmentId) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/mark_read`)
    .then(response => {
      $_track('read')
      return response.data
    }, () => null)
}
