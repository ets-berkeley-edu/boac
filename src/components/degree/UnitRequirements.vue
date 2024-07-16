<template>
  <v-container v-if="render" class="pl-0 py-1" fluid>
    <v-row>
      <v-col>
        <div class="align-items-start d-flex flex-row justify-space-between">
          <h3
            class="font-weight-bold pb-0 pr-2 text-no-wrap"
            :class="{'font-size-14': printable, 'font-size-20': !printable}"
          >
            Unit Requirements
          </h3>
          <div v-if="currentUser.canEditDegreeProgress && !degreeStore.sid && !printable">
            <v-btn
              id="unit-requirement-create-link"
              class="pr-0 py-0"
              :disabled="degreeStore.disableButtons"
              variant="text"
              @click.prevent="onClickAdd"
            >
              <div class="align-center d-flex justify-space-between">
                <div class="pr-2 text-no-wrap">
                  Add unit requirement
                </div>
                <div>
                  <v-icon class="font-size-16" :icon="mdiPlus" />
                </div>
              </div>
            </v-btn>
          </div>
        </div>
        <div v-if="!isEditing">
          <div
            v-if="!items.length"
            id="unit-requirements-no-data"
            class="no-data-text pl-1"
          >
            No unit requirements created
          </div>
          <!--
          TODO:
            thead-class="border-bottom"
          -->
          <v-data-table
            id="unit-requirements-table"
            :cell-props="data => {
              const align = data.column.key === 'completed' ? 'text-right' : ''
              const fontSize = printable ? 'font-size-12' : 'font-size-16'
              const padding = ['name', 'minUnits'].includes(data.column.key) ? 'pl-0 pr-1 pt-1' : 'px-0'
              return {class: `${align} font-size-12 ${padding} ${fontSize} text-uppercase border-t-sm`}
            }"
            density="compact"
            disable-sort
            :headers="headers"
            hide-default-footer
            :items="_filter(items, item => item.type === 'unitRequirement' || item.isExpanded)"
            :items-per-page="-1"
            mobile-breakpoint="md"
            :row-props="data => {
              const id = data.item.id
              // TODO: data.item.parent.id
              const parentId = 'data.item.parent.id'
              return {
                id: data.item.type === 'course' ? `unit-requirement-${parentId}-course-${id}` : `unit-requirement-${id}`
              }
            }"
          >
            <template v-if="degreeStore.sid && !printable" #item.name="{item}">
              <div v-if="item.type === 'course'" class="pl-3">
                {{ item.name }}
              </div>
              <v-btn
                v-if="item.type === 'unitRequirement'"
                :id="`unit-requirement-${item.id}-toggle`"
                class="border-0 p-0 d-block"
                :class="{'shadow-none': !item.isExpanded}"
                variant="text"
                @click.prevent="toggleExpanded(item)"
              >
                <div class="d-flex text-left">
                  <div class="caret caret-column pale-blue">
                    <v-icon :icon="item.isExpanded ? mdiMenuDown : mdiMenuRight" />
                  </div>
                  <div>
                    <span class="sr-only">{{ `${item.isExpanded ? 'Hide' : 'Show'} fulfillments of ` }}</span>
                    {{ item.name }}
                  </div>
                </div>
              </v-btn>
              <div
                v-if="item.isExpanded && item.type === 'unitRequirement' && !item.children.length"
                :id="`unit-requirement-${item.id}-no-courses`"
                class="text-grey pb-1 pl-4 pt-1"
              >
                No courses
              </div>
            </template>
            <template v-if="currentUser.canEditDegreeProgress && !degreeStore.sid && !printable" #item.actions="{item}">
              <div class="align-center d-flex">
                <v-btn
                  :id="`unit-requirement-${item.id}-edit-btn`"
                  class="pr-2 pt-0"
                  :disabled="degreeStore.disableButtons"
                  size="small"
                  variant="text"
                  @click.prevent="onClickEdit(item)"
                >
                  <v-icon :icon="mdiNoteEditOutline" />
                  <span class="sr-only">Edit {{ item.name }}</span>
                </v-btn>
              </div>
              <div>
                <v-btn
                  :id="`unit-requirement-${item.id}-delete-btn`"
                  class="px-0 pt-0"
                  :disabled="degreeStore.disableButtons"
                  size="small"
                  variant="text"
                  @click.prevent="onClickDelete(item)"
                >
                  <v-icon :icon="mdiTrashCanOutline" />
                  <span class="sr-only">Delete {{ item.name }}</span>
                </v-btn>
              </div>
            </template>
          </v-data-table>
        </div>
        <div v-if="isEditing" class="mb-3">
          <EditUnitRequirement :on-exit="reset" :unit-requirement="selected" />
        </div>
      </v-col>
    </v-row>
    <AreYouSureModal
      v-model="isDeleting"
      button-label-confirm="Delete"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      modal-header="Delete Unit Requirement"
    >
      Are you sure you want to delete <strong>{{ _get(selected, 'name') }}</strong>?
    </AreYouSureModal>
  </v-container>
</template>

<script setup>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import EditUnitRequirement from '@/components/degree/EditUnitRequirement'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {deleteUnitRequirement} from '@/api/degree'
import {mdiMenuDown, mdiMenuRight, mdiNoteEditOutline, mdiPlus, mdiTrashCanOutline} from '@mdi/js'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {useDegreeStore} from '@/stores/degree-edit-session'
import {useContextStore} from '@/stores/context'
import {onMounted, ref, watch} from 'vue'
import {each, filter as _filter, find, get, map, sortBy} from 'lodash'

const contextStore = useContextStore()
const degreeStore = useDegreeStore()

defineProps({
  printable: {
    required: false,
    type: Boolean
  }
})

const currentUser = contextStore.currentUser
const headers = []
const isDeleting = ref(false)
const isEditing = ref(false)
const items = ref(undefined)
const render = ref(false)
const selected = ref(undefined)

watch(() => degreeStore.lastPageRefreshAt, () => {
  refresh()
})

onMounted(() => {
  headers.push({
    key: 'name',
    headerProps: {class: 'font-size-12 pl-0 pr-1 text-no-wrap text-uppercase th-height'},
    title: 'Fulfillment Requirements'
  })
  headers.push({
    key: 'minUnits',
    headerProps: {class: 'font-size-12 pl-0 pr-1 text-no-wrap text-right text-uppercase th-height'},
    height: 20,
    title: degreeStore.sid ? 'Min' : 'Min Units'
  })
  if (degreeStore.sid) {
    headers.push({
      key: 'completed',
      headerProps: {class: 'font-size-12 px-0 text-no-wrap text-right text-uppercase th-height'},
      title: 'Completed'
    })
  } else if (currentUser.canEditDegreeProgress) {
    headers.push({
      key: 'actions',
      headerProps: {class: 'font-size-12 px-0 text-no-wrap text-uppercase th-height'}
    })
  }
  refresh()
  render.value = true
})

const deleteCanceled = () => {
  isDeleting.value = false
  putFocusNextTick(`unit-requirement-${get(selected.value, 'id')}-delete-btn`)
  alertScreenReader('Canceled. Nothing deleted.')
  degreeStore.setDisableButtons(false)
}

const deleteConfirmed = () => {
  const name = get(selected.value, 'name')
  const templateId = useDegreeStore().templateId
  deleteUnitRequirement(selected.value.id).then(() => {
    refreshDegreeTemplate(templateId).then(() => {
      alertScreenReader(`${name} deleted.`)
      isDeleting.value = false
      degreeStore.setDisableButtons(false)
      putFocusNextTick('unit-requirement-create-link')
    })
  })
}

const getUnitsCompleted = unitRequirement => {
  let count = 0
  each(degreeStore.courses, courses => {
    each(courses, course => {
      if (course.categoryId) {
        each(course.unitRequirements, u => {
          if (u.id === unitRequirement.id) {
            count += course.units
          }
        })
      }
    })
  })
  return count
}

const onClickAdd = () => {
  degreeStore.setDisableButtons(true)
  selected.value = null
  isEditing.value = true
}

const onClickDelete = item => {
  degreeStore.setDisableButtons(true)
  selected.value = item
  isDeleting.value = true
}

const onClickEdit = item => {
  degreeStore.setDisableButtons(true)
  selected.value = item
  isEditing.value = true
}

const refresh = () => {
  const expandedIds = map((_filter(items.value, 'isExpanded')), 'id')
  const values = []
  each(degreeStore.unitRequirements, u => {
    const isExpanded = expandedIds.includes(u.id)
    const unitRequirement = {
      id: u.id,
      children: [],
      completed: getUnitsCompleted(u),
      isExpanded,
      minUnits: u.minUnits,
      name: u.name,
      type: 'unitRequirement'
    }
    values.push(unitRequirement)
    if (degreeStore.sid) {
      let courses = _filter(degreeStore.courses.assigned, course => {
        return !!find(course.unitRequirements, ['id', u.id])
      })
      courses = sortBy(courses, ['name', 'id'])
      each(courses, course => {
        const child = {
          id: course.id,
          completed: course.units,
          isExpanded,
          name: course.name,
          parent: {id: unitRequirement.id},
          type: 'course'
        }
        values.push(child)
        unitRequirement.children.push(child)
      })
    }
  })
  items.value = values
}

const reset = () => {
  degreeStore.setDisableButtons(false)
  selected.value = null
  isEditing.value = false
  const focusId = selected.value ? `unit-requirement-${selected.value.id}-edit-btn` : 'unit-requirement-create-link'
  putFocusNextTick(focusId)
}

const toggleExpanded = item => {
  const value = !item.isExpanded
  item.isExpanded = value
  each(item.children, child => child.isExpanded = value)
}
</script>

<style scoped>
.caret-column {
  width: 1.3rem;
}
</style>
