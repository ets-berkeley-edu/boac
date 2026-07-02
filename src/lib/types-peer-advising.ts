import type {PeerAdvisingDepartment} from '@/lib/types'

export type PeerAdvisorNoteCount = {
  deletedAt: string | undefined,
  name: string,
  noteCount: number,
  uid: string
}

export type Month = {
  label: string,
  month: number,
  year: number
}

export interface PeerAdvisingReportTimeframe extends Month {
  noteCount: number,
  peerAdvisors: PeerAdvisorNoteCount[],
}

export type PeerAdvisingHistoricalReport = {
  label: string,
  months: PeerAdvisingReportTimeframe[]
}[]

export type PeerAdvisingManagerReport = {
  currentMonth: PeerAdvisingReportTimeframe,
  distinctPeerAdvisorAuthors: number,
  noteTemplates: {
    id: number,
    title: string,
    usageCount: number
  }[],
  noteTopics: {
    id: number,
    topic: string,
    usageCount: number
  }[],
  peerAdvisingDepartment: PeerAdvisingDepartment,
  totalPeerAdvisingNoteCount: number
}
