<template>
  <div v-if="render" aria-labelledby="unit-requirements-header" role="region">
    <div class="align-center d-flex flex-row justify-space-between">
      <h3
        id="unit-requirements-header"
        class="font-size-18 mb-1 mr-1 text-medium-emphasis text-no-wrap"
        :class="{'font-size-14': printable, 'font-size-20': !printable}"
      >
        Unit Requirements
      </h3>
      <div v-if="currentUser.canEditDegreeProgress && !degreeStore.sid && !printable">
        <v-btn
          id="unit-requirement-create-link"
          color="primary"
          :disabled="degreeStore.disableButtons"
          slim
          text="Add Unit Requirement"
          variant="text"
          :append-icon="mdiPlus"
          @click.prevent="onClickAdd"
        />
      </div>
    </div>
    <div v-if="!isEditing" class="py-1" :class="{'border-b-sm': size(items) && !printable}">
      <div
        v-if="!size(items)"
        id="unit-requirements-no-data"
        class="no-data-text my-2 pl-1"
      >
        No unit requirements created
      </div>
      <table v-if="size(items)" id="unit-requirements-table" class="unit-requirements-table">
        <caption class="sr-only">Unit Requirements</caption>
        <thead class="border-b-sm">
          <tr>
            <th
              id="th-unit-requirements-name"
              class="font-size-12 text-uppercase th-name th-height"
            >
              Fulfillment Requirements
            </th>
            <th
              id="th-unit-requirements-min-units"
              class="font-size-12 pr-3 text-no-wrap text-right text-uppercase th-height th-units"
              :class="{'th-min-units': !degreeStore.sid}"
            >
              {{ degreeStore.sid ? 'Min' : 'Min Units' }}
            </th>
            <th
              v-if="degreeStore.sid"
              id="th-unit-requirements-completed"
              class="font-size-12 text-right text-uppercase th-height th-completed"
            >
              Completed
            </th>
            <th
              v-if="!degreeStore.sid && currentUser.canEditDegreeProgress && !props.printable"
              id="th-unit-requirements-actions"
              class="px-0 th-actions th-height"
            >
              <span class="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, index) in _filter(items, row => row.type === 'unitRequirement' || row.isExpanded)"
            :id="item.type === 'course' ? `unit-requirement-${item.parent.id}-course-${item.id}` : `unit-requirement-${item.id}`"
            :key="index"
          >
            <td class="overflow-wrap-break-word" :class="{'font-size-12': printable, 'font-size-16': !printable}">
              <div v-if="!degreeStore.sid || printable" class="mr-1">
                {{ item.name }}
              </div>
              <div v-if="degreeStore.sid && !printable">
                <div v-if="item.type === 'course'" class="pl-6 pb-2" :class="{'demo-mode-blur': currentUser.inDemoMode}">
                  {{ item.name }}
                </div>
                <button
                  v-if="item.type === 'unitRequirement'"
                  :id="`unit-requirement-${item.id}-toggle`"
                  :aria-expanded="item.isExpanded"
                  class="align-start d-flex text-left text-primary unit-requirement-toggle"
                  @click.prevent="toggleExpanded(item)"
                >
                  <v-icon color="primary" :icon="item.isExpanded ? mdiMenuDown : mdiMenuRight" />
                  <span class="sr-only">{{ `${item.isExpanded ? 'Hide' : 'Show'} fulfillments of ` }}</span>
                  {{ item.name }}
                </button>
                <v-expand-transition>
                  <div
                    v-if="item.isExpanded && item.type === 'unitRequirement' && !item.children.length"
                    :id="`unit-requirement-${item.id}-no-courses`"
                    class="text-surface-variant pl-6 pb-2"
                  >
                    No courses
                  </div>
                </v-expand-transition>
              </div>
            </td>
            <td
              class="pr-3 py-1 text-right"
              :class="{
                'font-size-12': printable,
                'font-size-16': !printable
              }"
            >
              <div class="w-100">
                {{ item.minUnits }}
              </div>
            </td>
            <td
              v-if="degreeStore.sid"
              class="text-right"
              :class="{
                'font-size-12': printable,
                'font-size-16': !printable
              }"
            >
              {{ item.completed }}
            </td>
            <td
              v-if="currentUser.canEditDegreeProgress && !degreeStore.sid && !printable"
              class="font-size-16"
            >
              <div class="d-flex justify-end">
                <div class="degree-check-action-buttons align-center d-flex text-no-wrap">
                  <v-btn
                    :id="`unit-requirement-${item.id}-edit-btn`"
                    :aria-label="`Edit ${item.name}`"
                    :class="{'text-primary': !degreeStore.disableButtons}"
                    color="transparent"
                    density="compact"
                    :disabled="degreeStore.disableButtons"
                    flat
                    :icon="mdiNoteEditOutline"
                    size="small"
                    title="Edit"
                    @click.prevent="() => onClickEdit(item)"
                  />
                  <v-btn
                    :id="`unit-requirement-${item.id}-delete-btn`"
                    :aria-label="`Delete ${item.name}`"
                    :class="{'text-primary': !degreeStore.disableButtons}"
                    color="transparent"
                    density="compact"
                    :disabled="degreeStore.disableButtons"
                    flat
                    :icon="mdiTrashCan"
                    size="small"
                    title="Delete"
                    @click.prevent="onClickDelete(item)"
                  />
                </div>
              </div>
              <AreYouSureModal
                v-model="isDeleting"
                button-label-confirm="Delete"
                :function-cancel="deleteCanceled"
                :function-confirm="deleteConfirmed"
                modal-header="Delete Unit Requirement"
              >
                Are you sure you want to delete <strong>{{ get(selected, 'name') }}</strong>?
              </AreYouSureModal>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="isEditing" class="mb-3">
      <EditUnitRequirement :on-exit="reset" :unit-requirement="selected" />
    </div>
  </div>
</template>

<script setup>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import EditUnitRequirement from '@/components/degree/EditUnitRequirement'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {deleteUnitRequirement} from '@/api/degree'
import {filter as _filter, each, find, get, map, size, sortBy} from 'lodash'
import {mdiMenuDown, mdiMenuRight, mdiNoteEditOutline, mdiPlus, mdiTrashCan} from '@mdi/js'
import {onMounted, ref, watch} from 'vue'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session'

const contextStore = useContextStore()
const degreeStore = useDegreeStore()

const props = defineProps({
  printable: {
    required: false,
    type: Boolean
  }
})

const currentUser = contextStore.currentUser
const isDeleting = ref(false)
const isEditing = ref(false)
const items = ref({})
const render = ref(false)
const selected = ref(undefined)

watch(() => degreeStore.lastPageRefreshAt, () => {
  refresh()
})

onMounted(() => {
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
  alertScreenReader('Deleting')
  deleteUnitRequirement(selected.value.id).then(() => {
    refreshDegreeTemplate(templateId).then(() => {
      alertScreenReader(`Deleted "${name}" unit requirement.`)
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
  // In addition to setting the children's expanded value, we also want to find the children in the main array and set their expanded state.
  items.value.forEach(itemInArray => {
    if (itemInArray.parent?.id === item.id) { // The question mark (optional chaining) here is because some of the items do not have a parent. We only want this IF statement for items that do have a parent.
      itemInArray.isExpanded = value
    }
  })
}
</script>

<style scoped>
table {
  border-collapse: collapse;
  table-layout: fixed;
  width: 100%;
}
td {
  height: 25px;
  padding-top: 3px;
  vertical-align: top;
}
th {
  height: 20px;
  padding-bottom: 5px;
}
.th-actions {
  width: 10%;
}
.th-completed {
  width: 25%;
}
.th-min-units {
  width: 20% !important;
}
.th-name {
  width: 55%;
}
.th-units {
  width: 15%;
}
.unit-requirements-table {
  min-width: 250px;
}
.unit-requirement-toggle {
  max-width: 200px;
}
</style>
