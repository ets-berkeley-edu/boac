import axios from 'axios'
import {each, get} from 'lodash'
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

const $_onUpdate = (curatedGroups: any[]) => {
  each(curatedGroups, curatedGroup => {
    useContextStore().updateMyCuratedGroup(curatedGroup)
  })
  useContextStore().broadcast('my-curated-groups-updated', curatedGroups[0].domain)
  $_track('update')
}

export function addStudentsToCuratedGroups(curatedGroupIds: number[], sids: string[], returnStudentProfiles?: boolean) {
  const url: string = `${utils.apiBaseUrl()}/api/curated_group/students/add`
  return axios.post(url, {curatedGroupIds, sids, returnStudentProfiles}).then(response => {
    $_onUpdate(response.data)
    return response.data
  })
}

export function createCuratedGroup(domain: string, name: string, sids: string[]) {
  const url: string = `${utils.apiBaseUrl()}/api/curated_group/create`
  return axios.post(url, {domain, name, sids}).then(function(response) {
    $_onCreate(response.data)
    return response.data
  })
}

export function deleteCuratedGroup(domain: string, curatedGroupId: number) {
  const url: string = `${utils.apiBaseUrl()}/api/curated_group/delete/${curatedGroupId}`
  const headers = {'Content-Type': 'application/json'}
  return axios.delete(url, {headers}).then(() => {
    $_onDelete(domain, curatedGroupId)
    $_track('delete')
  })
}

export function downloadCuratedGroupCsv(curatedGroupId: number, name: string, csvColumnsSelected: any[]) {
  const now = DateTime.now().toFormat('yyyy-MM-dd_HH-mm-ss')
  const filename = name ? `${name}-students-${now}` : `students-${now}`
  const termId = useContextStore().currentUser.preferences.termId || get(useContextStore().config, 'currentEnrollmentTermId')

  $_track('download', filename)
  const url: string = `${utils.apiBaseUrl()}/api/curated_group/${curatedGroupId}/download_csv`
  return axios.post(url, {curatedGroupId, csvColumnsSelected, termId}).then(response => {
    return fileDownload(response.data, `${filename}.csv`)
  })
}

export function getCuratedGroup(
  curatedGroupId: number,
  limit: number,
  offset: number,
  orderBy: string,
  termId: string | undefined
) {
  $_track('view')
  const url: string = `${utils.apiBaseUrl()}/api/curated_group/${curatedGroupId}?orderBy=${orderBy}&termId=${termId}&offset=${offset}&limit=${limit}`
  return axios.get(url).then(response => response.data)
}

export function getUsersWithCuratedGroups() {
  return axios.get(`${utils.apiBaseUrl()}/api/curated_groups/all`).then(response => response.data)
}

export function removeFromCuratedGroups(curatedGroupIds: number[], sid: any) {
  const url: string = `${utils.apiBaseUrl()}/api/curated_group/remove_student/${sid}`
  return axios.post(url, {curatedGroupIds}).then(response => {
    const data = response.data
    $_onUpdate(data)
    return data
  })
}

export function renameCuratedGroup(curatedGroupId: number, name: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/curated_group/rename`, {id: curatedGroupId, name}).then(response => {
    const data = response.data
    $_onUpdate([data])
    return data
  })
}

export function getStudentsWithAlerts(curatedGroupId: number) {
  const url: string = `${utils.apiBaseUrl()}/api/curated_group/${curatedGroupId}/students_with_alerts`
  return axios.get(url).then(response => response.data)
}
