import {defineStore, StoreDefinition} from 'pinia'
import {get} from 'lodash'

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

export const useDegreeStore: StoreDefinition = defineStore('degree', {
  state: () => ({
    addCourseMenuOptions: undefined,
    categories: undefined,
    courses: undefined,
    createdAt: undefined,
    createdBy: undefined,
    degreeName: undefined,
    degreeNote: undefined,
    disableButtons: false,
    dismissedAlerts: [] as number[],
    draggingContext: {
      course: undefined,
      dragContext: undefined,
      target: undefined
    },
    includeNotesWhenPrint: true,
    lastPageRefreshAt: undefined as Date | undefined,
    parentTemplateId: undefined,
    parentTemplateUpdatedAt: undefined,
    sid: undefined,
    templateId: NaN as number,
    unitRequirements: undefined,
    updatedAt: undefined,
    updatedBy: undefined
  }),
  getters: {
    degreeEditSessionToString: state => ({
      categories: state.categories,
      courses: state.courses,
      degreeName: state.degreeName,
      degreeNote: state.degreeNote,
      disableButtons: state.disableButtons,
      templateId: state.templateId,
      unitRequirements: state.unitRequirements
    }),
    isUserDragging: (state, courseId: number) => {
      return !!courseId && get(state.draggingContext, 'course.id') === courseId
    }
  },
  actions: {
    draggingContextReset() {
      this.draggingContext = $_getDefaultDraggingContext()
    },
    dragStart(course, dragContext) {
      this.draggingContext = {course, dragContext, target: undefined}
    },
    dismissAlert(templateId: number) {
      this.dismissedAlerts.push(templateId)
    },
    resetSession(template: any) {
      this.disableButtons = false
      this.draggingContext = $_getDefaultDraggingContext()
      if (template) {
        this.categories = template.categories
        this.courses = template.courses
        this.createdAt = template.createdAt
        this.createdBy = template.createdBy
        this.degreeName = template.name
        this.degreeNote = template.note
        this.parentTemplateId = template.parentTemplateId
        this.parentTemplateUpdatedAt = template.parentTemplateUpdatedAt
        this.sid = template.sid
        this.templateId = template.id
        this.unitRequirements = template.unitRequirements
        this.updatedAt = template.updatedAt
        this.updatedBy = template.updatedBy
      } else {
        this.categories = this.createdAt = this.createdBy = this.degreeName = this.degreeNote = undefined
        this.parentTemplateId = this.parentTemplateUpdatedAt = undefined
        this.templateId = NaN
        this.sid = this.unitRequirements = this.updatedAt = this.updatedBy = undefined
      }
      this.lastPageRefreshAt = new Date()
    },
    setDisableButtons(disableAll: any) {
      this.disableButtons = disableAll
    },
    setDraggingTarget(target: any) {
      this.draggingContext.target = target
    },
    setIncludeNotesWhenPrint(include: any) {
      this.includeNotesWhenPrint = include
    }
  }
})
