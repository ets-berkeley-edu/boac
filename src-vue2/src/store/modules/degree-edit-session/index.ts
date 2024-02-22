import _ from 'lodash'

export type DegreeProgressCourses = {
  assigned: any[],
  unassigned: any[]
}

type DraggingContext = {
  course: any,
  dragContext: any,
  target: any
}

function $_getDefaultDraggingContext(): DraggingContext {
  return {
    course: undefined,
    dragContext: undefined,
    target: undefined
  }
}

const state = {
  addCourseMenuOptions: undefined,
  categories: undefined,
  courses: undefined,
  createdAt: undefined,
  createdBy: undefined,
  degreeName: undefined,
  degreeNote: undefined,
  disableButtons: false,
  dismissedAlerts: [],
  draggingContext: {
    course: undefined,
    dragContext: undefined,
    target: undefined
  },
  includeNotesWhenPrint: true,
  lastPageRefreshAt: undefined,
  parentTemplateId: undefined,
  parentTemplateUpdatedAt: undefined,
  sid: undefined,
  templateId: NaN,
  unitRequirements: undefined,
  updatedAt: undefined,
  updatedBy: undefined
}

const getters = {
  addCourseMenuOptions: (state: any): any[] => state.addCourseMenuOptions,
  categories: (state: any): any[] => state.categories,
  courses: (state: any): DegreeProgressCourses => state.courses,
  createdAt: (state: any): any[] => state.createdAt,
  createdBy: (state: any): any[] => state.createdBy,
  degreeEditSessionToString: (state: any): any => ({
    categories: state.categories,
    courses: state.courses,
    degreeName: state.degreeName,
    degreeNote: state.degreeNote,
    disableButtons: state.disableButtons,
    templateId: state.templateId,
    unitRequirements: state.unitRequirements
  }),
  degreeName: (state: any): string => state.degreeName,
  degreeNote: (state: any): string => state.degreeNote,
  disableButtons: (state: any): boolean => state.disableButtons,
  dismissedAlerts: (state: any): number[] => state.dismissedAlerts,
  draggingContext: (state: any): any => state.draggingContext,
  includeNotesWhenPrint: (state: any): boolean => state.includeNotesWhenPrint,
  isUserDragging: (state: any) => (courseId: number) => !!courseId && _.get(state.draggingContext.course, 'id') === courseId,
  lastPageRefreshAt: (state: any): any[] => state.lastPageRefreshAt,
  parentTemplateId: (state: any): string => state.parentTemplateId,
  parentTemplateUpdatedAt: (state: any): string => state.parentTemplateUpdatedAt,
  sid: (state: any): string => state.sid,
  templateId: (state: any): number => state.templateId,
  unitRequirements: (state: any): any[] => state.unitRequirements,
  updatedAt: (state: any): any[] => state.updatedAt,
  updatedBy: (state: any): any[] => state.updatedBy
}

const mutations = {
  draggingContextReset: (state: any) => state.draggingContext = $_getDefaultDraggingContext(),
  dragStart: (state: any, {course, dragContext}) => state.draggingContext = {course, dragContext, target: undefined},
  dismissAlert: (state: any, templateId: number) => state.dismissedAlerts.push(templateId),
  resetSession: (state: any, template: any) => {
    state.disableButtons = false
    state.draggingContext = $_getDefaultDraggingContext()
    if (template) {
      state.categories = template.categories
      state.courses = template.courses
      state.createdAt = template.createdAt
      state.createdBy = template.createdBy
      state.degreeName = template.name
      state.degreeNote = template.note
      state.parentTemplateId = template.parentTemplateId
      state.parentTemplateUpdatedAt = template.parentTemplateUpdatedAt
      state.sid = template.sid
      state.templateId = template.id
      state.unitRequirements = template.unitRequirements
      state.updatedAt = template.updatedAt
      state.updatedBy = template.updatedBy
    } else {
      state.categories = state.createdAt = state.createdBy = state.degreeName = state.degreeNote = undefined
      state.parentTemplateId = state.parentTemplateUpdatedAt = undefined
      state.templateId = state.sid = state.unitRequirements = state.updatedAt = state.updatedBy = undefined
    }
    state.lastPageRefreshAt = new Date()
  },
  setDisableButtons: (state: any, disableAll: any) => state.disableButtons = disableAll,
  setDraggingTarget: (state: any, target: any) => state.draggingContext.target = target,
  setIncludeNotesWhenPrint: (state: any, include: any) => state.includeNotesWhenPrint = include
}

export default {
  getters,
  namespaced: true,
  mutations,
  state
}
