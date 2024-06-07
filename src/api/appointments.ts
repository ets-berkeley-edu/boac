import axios from 'axios'
import ga from '@/lib/ga'
import utils from '@/api/api-utils'

const $_track = action => ga.appointment(action)

export function markAppointmentRead(appointmentId) {
  const url: string = `${utils.apiBaseUrl()}/api/appointments/${appointmentId}/mark_read`
  return axios.post(url).then(response => {
    $_track('read')
    return response.data
  })
}
