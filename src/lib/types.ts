export type Attachment = {
  displayName: string,
  id: number,
  name: string,
  size: number
}

export type BoaConfig = {
  academicStandingDescriptions: object,
  apiBaseUrl: string,
  currentEnrollmentTerm: string,
  currentEnrollmentTermId: number,
  defaultTermUnitsAllowed: {
    max: number,
    min: number
  },
  devAuthEnabled: boolean,
  draftNoteSubjectPlaceholder: string,
  fixedWarningOnAllPages: boolean,
  gaMeasurementId: string,
  isProduction: boolean,
  isVueAppDebugMode: boolean,
  maxAttachmentsPerNote: number,
  notesDraftAutoSaveInterval: number,
  supportEmailAddress: string,
  timezone: string
}

export type BoaUser = {
  id: number | undefined,
  automateDegreeProgressPermission: boolean,
  canAccessAdmittedStudents: boolean,
  canAccessAdvisingData: boolean,
  canAccessCanvasData: boolean,
  canEditDegreeProgress: boolean,
  canReadDegreeProgress: boolean,
  degreeProgressPermission: string | undefined,
  deletedAt: Date | undefined,
  departments: BoaUserDepartment[],
  inDemoMode: boolean,
  isAdmin: boolean,
  isAuthenticated: boolean,
  isBlocked: boolean,
  isDemoModeAvailable: boolean,
  myCohorts: Cohort[],
  myCuratedGroups: CuratedGroup[],
  myDraftNoteCount: number | undefined,
  name: string | undefined,
  preferences: {
    termId: string | undefined
  },
  title: string | undefined,
  uid: string | undefined
}

export interface BoaUserDepartment extends HasDeptCode {
  id: number,
  memberships: DepartmentMembership[]
}

export type BoaUsersFilter = {
  deptCode: string | undefined,
  peerAdvisingDepartmentId: number | undefined,
  role: string,
  searchPhrase: string,
  status: string,
  type: string
}

export type Cohort = {
  domain: string,
  id: number,
  name: string
}

export type CuratedGroup = {
  domain: string,
  id: number,
  name: string
}

export type Course = {
  sections: Section[],
  waitlisted: boolean
}

export type CourseRequirement = {
  categoryType: ('Course Requirement' | 'Campus Requirement'),
  courses: DegreeProgressCourse[],
  id: number
}

export type Category = {
  categoryType: 'Category',
  courseRequirements: CourseRequirement[],
  courses: DegreeProgressCourse[],
  id: number,
  name: string,
  subcategories: Category[]
}

export type DegreeProgressCourse = {
  id: number,
  manuallyCreatedAt: string,
  manuallyCreatedBy: number,
  sectionId: number,
  sis: {
    units: number
  },
  termId: number,
  units: number
}

export type DegreeProgressCourses = {
  assigned: DegreeProgressCourse[],
  unassigned: DegreeProgressCourse[]
}

export type DegreeTemplate = {
  categories: object[] | undefined,
  courses: DegreeProgressCourse[] | undefined,
  createdAt: string | undefined,
  createdBy: string | undefined,
  id: number,
  name: string | undefined,
  note: string | undefined,
  parentTemplateId: string | undefined,
  parentTemplateUpdatedAt: string | undefined,
  sid: string | undefined,
  unitRequirements: object[] | undefined,
  updatedAt: string | undefined,
  updatedBy: string | undefined
}

export interface Department extends HasDeptCode {
  id: number,
  peerAdvisingDepartments: PeerAdvisingDepartment[]
}

export type DepartmentMembership = {
  automateMembership?: boolean,
  peerAdvisingDepartmentId?: number,
  peerAdvisingDepartmentName?: string,
  role: DepartmentMembershipRole
}

export type DepartmentMembershipRole = 'advisor' | 'director' | 'peer_advisor' | 'peer_advisor_manager'

export type DraggingContext = {
  course: DegreeProgressCourse | undefined,
  dragContext: unknown | undefined,
  target: unknown | undefined
}

export type ExportListOption = {
  text: string,
  value: string,
  disabled?: boolean
}

export interface HasDeptCode {
  deptCode: string,
  deptName: string
}

export type NoteEditSessionModel = {
  attachments: Attachment[],
  author: object,
  body?: string,
  contactType?: string | null,
  deleteAttachmentIds: number[],
  id: number,
  isDraft: boolean,
  isPrivate: boolean,
  setDate?: string,
  subject?: string,
  topics: string[]
}

export type NoteRecipients = {
  cohorts: Cohort[],
  curatedGroups: CuratedGroup[],
  sids: string[]
}

export type NoteTemplate = {
  id: number,
  title: string
}

export type Pagination = {
  currentPage: number,
  itemsPerPage: number
}

export type PeerAdvisingDepartment = {
  id: number,
  name: string
}

export type ScreenReaderAlert = {
  message: string,
  politeness: string
}

export type Section = {
  enrollmentStatus: string,
  gradingBasis: string,
  incompleteComments: string,
  incompleteLapseGradeDate: string,
  incompleteStatusCode: string
}

export type SelectOption<T> = {
  disabled?: boolean,
  text: string,
  value: T
}

export type ServiceAnnouncement = {
  isPublished: boolean,
  text: string
}

export type Student = {
  sid: string
}
