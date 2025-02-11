import type {StoreDefinition} from 'pinia'
import {defineStore} from 'pinia'
import {get} from 'lodash'
import type {DegreeProgressCourse, DegreeTemplate, DraggingContext} from '@/lib/types'

function $_getDefaultDraggingContext(): DraggingContext {
  return {
    course: undefined as DegreeProgressCourse | undefined,
    dragContext: undefined as unknown | undefined,
    target: undefined as unknown | undefined
  }
}

export const useDegreeStore: StoreDefinition = defineStore('degree', {
  state: () => ({
    addCourseMenuOptions: undefined,
    categories: undefined as object[] | undefined,
    courses: undefined as DegreeProgressCourse[] | undefined,
    createdAt: undefined as string | undefined,
    createdBy: undefined as string | undefined,
    degreeName: undefined as string | undefined,
    degreeNote: undefined as string | undefined,
    disableButtons: false,
    dismissedAlerts: [] as number[],
    draggingContext: {
      course: undefined as DegreeProgressCourse | undefined,
      dragContext: undefined as unknown | undefined,
      target: undefined as unknown | undefined
    },
    includeNotesWhenPrint: true,
    lastPageRefreshAt: undefined as Date | undefined,
    parentTemplateId: undefined as string | undefined,
    parentTemplateUpdatedAt: undefined as string | undefined,
    sid: undefined as string | undefined,
    templateId: NaN as number,
    unitRequirements: undefined as object[] | undefined,
    updatedAt: undefined as string | undefined,
    updatedBy: undefined as string | undefined
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
    draggingCourseId: state => get(state.draggingContext, 'course.id')
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
    resetSession(template: DegreeTemplate) {
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
    setDisableButtons(disableAll: boolean) {
      this.disableButtons = disableAll
    },
    setDraggingTarget(target: unknown | undefined) {
      this.draggingContext.target = target
    },
    setIncludeNotesWhenPrint(include: boolean) {
      this.includeNotesWhenPrint = include
    }
  }
})
