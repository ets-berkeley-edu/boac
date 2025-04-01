import type {BoaUser, PeerAdvisingDepartment} from '@/lib/types'

export type Month = {
  label: string,
  month: number,
  year: number
}

export interface PeerAdvisingReportTimeframe extends Month {
  noteCount: number,
  peerAdvisors: BoaUser[],
}

export type PeerAdvisingHistoricalReport = {
  label: string,
  months: PeerAdvisingReportTimeframe[]
}[]

export type PeerAdvisingManagerReport = {
  currentMonth: PeerAdvisingReportTimeframe,
  distinctPeerAdvisorAuthors: number,
  noteTemplates: {
    name: string,
    noteTemplateUsageCount: number,
    templateTitle: string
  }[],
  peerAdvisingDepartment: PeerAdvisingDepartment,
  totalPeerAdvisingNoteCount: number
}
