import {orderBy} from 'lodash'
import type {PeerAdvisorNoteCount} from '@/lib/types-peer-advising'

export type PeerAdvisorSortBy = 'name' | 'noteCount'

export type PeerAdvisorSortOptions = {
  sortBy: PeerAdvisorSortBy,
  sortDesc: boolean
}

export const defaultPeerAdvisorSortOptions = (): PeerAdvisorSortOptions => ({sortBy: 'noteCount', sortDesc: true})

const nameSorter = (peerAdvisor: PeerAdvisorNoteCount) => (peerAdvisor.name || '').toLowerCase()

export const sortPeerAdvisors = (
  peerAdvisors: PeerAdvisorNoteCount[],
  {sortBy, sortDesc}: PeerAdvisorSortOptions
): PeerAdvisorNoteCount[] => {
  const direction = sortDesc ? 'desc' : 'asc'

  if (sortBy === 'name') {
    return orderBy(peerAdvisors, [nameSorter], [direction])
  }
  return orderBy(
    peerAdvisors,
    [peerAdvisor => peerAdvisor.noteCount || 0, nameSorter],
    [direction, 'asc']
  )
}

export const getPeerAdvisorAriaSort = (
  column: 'name' | 'noteCount',
  {sortBy, sortDesc}: PeerAdvisorSortOptions
): 'ascending' | 'descending' | 'none' => {
  if (column === 'name' && sortBy === 'name') {
    return sortDesc ? 'descending' : 'ascending'
  }
  if (column === 'noteCount' && sortBy === 'noteCount') {
    return sortDesc ? 'descending' : 'ascending'
  }
  return 'none'
}

export const togglePeerAdvisorSort = (
  column: 'name' | 'noteCount',
  current: PeerAdvisorSortOptions
): PeerAdvisorSortOptions => {
  if (column === 'name') {
    if (current.sortBy === 'name') {
      return {...current, sortDesc: !current.sortDesc}
    }
    return {sortBy: 'name', sortDesc: false}
  }
  if (current.sortBy === 'noteCount') {
    return {...current, sortDesc: !current.sortDesc}
  }
  return {sortBy: 'noteCount', sortDesc: true}
}
