import {get, remove} from 'lodash'
import axios from 'axios'
import ga from '@/lib/ga'
import {DateTime} from 'luxon'
import utils from '@/api/api-utils'
import {useContextStore} from '@/stores/context'
import fileDownload from 'js-file-download'

const $_track = (action, label?) => ga.cohort(action, label)

const $_onCreate = (group: any) => {
  useContextStore().addMyCuratedGroup(group)
  useContextStore().broadcast('my-curated-groups-updated', group.domain)
  $_track('create')
}

const $_onDelete = (domain: string, curatedGroupId: number) => {
  useContextStore().removeMyCuratedGroup(curatedGroupId)
  useContextStore().broadcast('my-curated-groups-updated', domain)
  $_track('delete')
}

const $_onUpdate = (curatedGroup: any) => {
  useContextStore().updateMyCuratedGroup(curatedGroup)
  useContextStore().broadcast('my-curated-groups-updated', curatedGroup.domain)
  $_track('update')
}

export function addStudentsToCuratedGroup(curatedGroupId: number, sids: string[], returnStudentProfiles?: boolean) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/curated_group/students/add`, {
      curatedGroupId: curatedGroupId,
      sids: sids,
      returnStudentProfiles: returnStudentProfiles
    })
    .then(data => {
      $_onUpdate(data)
      return data
    })
}

export function createCuratedGroup(domain: string, name: string, sids: string[]) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/curated_group/create`, {domain, name, sids})
    .then(function(data) {
      $_onCreate(data)
      return data
    })
}

export function deleteCuratedGroup(domain: string, curatedGroupId: number) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/curated_group/delete/${curatedGroupId}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(() => {
      $_onDelete(domain, curatedGroupId)
      $_track('delete')
    })
    .catch(error => error)
}

export function downloadCuratedGroupCsv(curatedGroupId: number, name: string, csvColumnsSelected: any[]) {
  const now = DateTime.now().toFormat('yyyy-MM-dd_HH-mm-ss')
  const filename = name ? `${name}-students-${now}` : `students-${now}`
  const termId = useContextStore().currentUser.preferences.termId || get(useContextStore().config, 'currentEnrollmentTermId')

  $_track('download', filename)
  return axios
    .post(`${utils.apiBaseUrl()}/api/curated_group/${curatedGroupId}/download_csv`, {
      curatedGroupId,
      csvColumnsSelected,
      termId
    })
    .then(response => fileDownload(response.data, `${filename}.csv`))
}

export function getCuratedGroup(
  curatedGroupId: number,
  limit: number,
  offset: number,
  orderBy: string,
  termId: string | undefined
) {
  $_track('view')
  const url = `${utils.apiBaseUrl()}/api/curated_group/${curatedGroupId}?orderBy=${orderBy}&termId=${termId}&offset=${offset}&limit=${limit}`
  return axios.get(url).then(data => data, () => null)
}

export function getUsersWithCuratedGroups() {
  return axios.get(`${utils.apiBaseUrl()}/api/curated_groups/all`).then(response => response.data, () => null)
}

export function removeFromCuratedGroup(curatedGroupId: number, sid: any) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/curated_group/${curatedGroupId}/remove_student/${sid}`)
    .then(response => {
      const group = response.data
      $_onUpdate(group)
      if (group.students) {
        group.students = remove(group.students, (student: any) => sid === (student.sid || student.csEmplId))
      }
      return group
    })
}

export function renameCuratedGroup(curatedGroupId: number, name: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/curated_group/rename`, {id: curatedGroupId, name})
    .then(response => {
      $_onUpdate(response)
      return response
    })
    .catch(error => error)
}

export function getStudentsWithAlerts(curatedGroupId: number) {
  const url = `${utils.apiBaseUrl()}/api/curated_group/${curatedGroupId}/students_with_alerts`
  return axios.get(url).then(response => response, () => null)
}
