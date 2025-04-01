export type Attachment = {
  displayName: string,
  id: number,
  name: string,
  size: number
}

export interface BasicStudent extends HasName {
  sid: string,
  uid: string
}

export interface BasicStudentLabeled extends BasicStudent {label: string}

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
  noteContactTypes: NoteContactType[],
  notesDraftAutoSaveInterval: number,
  pingFrequency: number,
  supportEmailAddress: string,
  timezone: string
}

export interface BoaUser extends CalNetUser {
  id: number,
  automateDegreeProgressPermission: boolean,
  canAccessAdmittedStudents: boolean,
  canAccessAdvisingData: boolean,
  canAccessCanvasData: boolean,
  canAccessPrivateNotes: boolean,
  canEditDegreeProgress: boolean,
  canReadDegreeProgress: boolean,
  createdAt: string,
  degreeProgressPermission: string | undefined,
  deletedAt: string | undefined,
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
  uid: string
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

export type CalNetUser = {
  campusEmail: string,
  email: string,
  'firstName': string,
  'isExpiredPerLdap': string,
  'lastName': string,
  'name': string | undefined,
  'csid': string,
  'title': string | undefined,
  'uid': string
}

export type Cohort = {
  domain: string,
  id: number,
  name: string,
  totalStudentCount: number
}

export type CuratedGroup = {
  domain: string,
  id: number,
  name: string,
  totalStudentCount: number
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

export type Enrollment = {
  displayName: string,
  sections: Section[],
  title: string,
  units: number
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

export interface HasName {
  firstName: string,
  lastName: string
}

export type Note = {
  id: number,
  attachments: NoteAttachment[],
  author: NoteAuthor,
  body: string,
  contactType: string,
  createdAt: string,
  deletedAt: string,
  isDraft: string,
  isPrivate: string,
  peerAdvisingDepartmentId: string,
  setDate: string,
  sid: string,
  student: BasicStudent,
  subject: string,
  topics: string[],
  updatedAt: string
}

export type NoteAttachment = {
  id: number,
  displayName: string,
  filename: string,
  uploadedBy: string,
}

export type NoteAuthor = {
  id: number,
  departments: HasDeptCode[],
  email: string,
  name: string,
  role: string,
  sid: string,
  uid: string
}

export type NoteContactType = {
  isAvailableToPeerAdvisors: boolean,
  value: string
}

export type NoteEditSessionModel = {
  attachments: Attachment[],
  author: object,
  body: string | undefined,
  contactType: string | undefined,
  deleteAttachmentIds: number[],
  id: number,
  isDraft: boolean,
  isPrivate: boolean,
  peerAdvisingDepartmentId: number | undefined,
  setDate: string | undefined,
  subject: string | undefined,
  topics: string[]
  noteTemplateId: number | undefined,
}

export type NoteRecipients = {
  cohorts?: Cohort[],
  curatedGroups?: CuratedGroup[],
  sids: string[]
}

export type NoteTemplate = {
  id: number,
  body: string,
  title: string,
  topics: string[]
}

export type NoteTopic = {
  topic: string
}

export type Pagination = {
  currentPage: number,
  itemsPerPage: number
}

export type PeerAdvisingDepartment = {
  id: number,
  name: string,
  universityDeptName: string,
  peerAdvisingDepartmentMembers: BoaUser[]
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
  incompleteStatusCode: string,
  sectionId: number,
  sectionNumber: number
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

export interface Student extends HasName {
  sid: string,
  uid: string,
  academicCareerStatus: string,
  academicStanding: string,
  alertCount?: number,
  degrees?: object[],
  enrollmentTerms: object
}

export type TermEnrollment = {
  termId: number,
  termName: string,
  enrollments: Enrollment[]
}
