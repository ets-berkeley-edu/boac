<template>
  <div v-if="render">
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
          color="primary"
          density="compact"
          :disabled="degreeStore.disableButtons"
          text="Add Unit Requirement"
          variant="text"
          :append-icon="mdiPlus"
          @click.prevent="onClickAdd"
        />
      </div>
    </div>
    <div v-if="!isEditing" class="border-b-sm mt-1 pb-1">
      <div
        v-if="!size(items)"
        id="unit-requirements-no-data"
        class="no-data-text pl-1"
      >
        No unit requirements created
      </div>
      <table id="unit-requirements-table" class="w-100">
        <thead class="border-b-sm">
          <tr>
            <th
              id="th-unit-requirements-name"
              class="font-size-12 text-uppercase th-height"
            >
              Fulfillment Requirements
            </th>
            <th
              id="th-unit-requirements-min-units"
              class="font-size-12 pr-3 text-uppercase th-height"
            >
              {{ degreeStore.sid ? 'Min' : 'Min Units' }}
            </th>
            <th
              v-if="degreeStore.sid"
              id="th-unit-requirements-completed"
              class="float-right font-size-12 text-uppercase th-height"
            >
              Completed
            </th>
            <th
              v-if="!degreeStore.sid && currentUser.canEditDegreeProgress && !props.printable"
              id="th-unit-requirements-actions"
              class="px-0 th-height"
            >
              <span class="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in _filter(items, row => row.type === 'unitRequirement' || row.isExpanded)"
            :id="item.type === 'course' ? `unit-requirement-${item.parent.id}-course-${item.id}` : `unit-requirement-${item.id}`"
            :key="item.id"
          >
            <td
              :class="{
                'font-size-12': printable,
                'font-size-16': !printable
              }"
            >
              <div v-if="!degreeStore.sid || printable" class="mr-1">
                {{ item.name }}
              </div>
              <div v-if="degreeStore.sid && !printable">
                <div v-if="item.type === 'course'" class="pl-3">
                  {{ item.name }}
                </div>
                <a
                  v-if="item.type === 'unitRequirement'"
                  :id="`unit-requirement-${item.id}-toggle`"
                  class="border-0 pa-0 text-decoration-none unit-requirement-toggle"
                  :class="{'shadow-none': !item.isExpanded}"
                  href="#"
                  @click.prevent="toggleExpanded(item)"
                >
                  <div class="align-start d-flex">
                    <v-icon :icon="item.isExpanded ? mdiMenuDown : mdiMenuRight" />
                    <div>
                      <span class="sr-only">{{ `${item.isExpanded ? 'Hide' : 'Show'} fulfillments of ` }}</span>
                      {{ item.name }}
                    </div>
                  </div>
                </a>
                <v-expand-transition>
                  <div
                    v-if="item.isExpanded && item.type === 'unitRequirement' && !item.children.length"
                    :id="`unit-requirement-${item.id}-no-courses`"
                    class="text-grey pl-6 py-2"
                  >
                    No courses
                  </div>
                </v-expand-transition>
              </div>
            </td>
            <td
              class="pr-3 text-right"
              :class="{
                'font-size-12': printable,
                'font-size-16': !printable
              }"
            >
              <div class="float-end w-100">
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
              class="align-center d-flex font-size-16 justify-end px-0"
            >
              <div>
                <v-btn
                  :id="`unit-requirement-${item.id}-edit-btn`"
                  :aria-label="`Edit ${item.name}`"
                  class="mx-1 text-primary"
                  density="compact"
                  :disabled="degreeStore.disableButtons"
                  flat
                  :icon="mdiNoteEditOutline"
                  size="small"
                  title="Edit"
                  @click.prevent="() => onClickEdit(item)"
                />
              </div>
              <div>
                <v-btn
                  :id="`unit-requirement-${item.id}-delete-btn`"
                  :aria-label="`Delete ${item.name}`"
                  class="text-primary"
                  density="compact"
                  :disabled="degreeStore.disableButtons"
                  flat
                  :icon="mdiTrashCan"
                  size="small"
                  title="Delete"
                  @click.prevent="onClickDelete(item)"
                />
                <AreYouSureModal
                  v-model="isDeleting"
                  button-label-confirm="Delete"
                  :function-cancel="deleteCanceled"
                  :function-confirm="deleteConfirmed"
                  modal-header="Delete Unit Requirement"
                >
                  Are you sure you want to delete <strong>{{ get(selected, 'name') }}</strong>?
                </AreYouSureModal>
              </div>
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
import {each, filter as _filter, find, get, map, size, sortBy} from 'lodash'
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
table {
  border-collapse: collapse;
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
.unit-requirement-toggle {
  max-width: 200px;
}
</style>
