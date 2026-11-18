<template>
  <ul
    :id="id"
    aria-label="People you can tag"
    class="user-tag-dropdown"
    role="listbox"
    :style="{top: `${position.top}px`, left: `${position.left}px`}"
    @mousedown.prevent
  >
    <!-- Cancelling mousedown anywhere in the list (rows, message row, padding) keeps focus in the editor, so a click
    here doesn't blur it and close the dropdown. -->
    <!-- role="none": a listbox may only contain options, and this row is a status message, not a choice. -->
    <li v-if="isLoading || message" class="user-tag-message" role="none">
      {{ isLoading ? 'Searching…' : message }}
    </li>
    <template v-else>
      <li
        v-for="(user, index) in users"
        :id="optionId(id, index)"
        :key="user.uid"
        :aria-selected="index === highlightedIndex"
        class="user-tag-option"
        :class="{'user-tag-option-highlighted': index === highlightedIndex}"
        role="option"
        @click="emit('select', user)"
      >
        <div class="user-tag-name">
          <!-- v-text escapes the name, and avoids stray whitespace between the pieces; names are never rendered as HTML. -->
          <component
            :is="part.isMatch ? 'strong' : 'span'"
            v-for="(part, partIndex) in nameParts(user.name)"
            :key="partIndex"
            v-text="part.text"
          />
        </div>
        <div v-if="subtitle(user)" class="user-tag-subtitle">{{ subtitle(user) }}</div>
      </li>
    </template>
  </ul>
</template>

<script setup lang="ts">
import {compact} from 'lodash'
import type {TaggableUser} from '@/lib/types'
import {optionId} from '@/lib/user-tags'

const emit = defineEmits<{
  (e: 'select', user: TaggableUser): void
}>()

const props = defineProps<{
  id: string
  users: TaggableUser[]
  highlightedIndex: number
  typedText: string
  message: string | null
  isLoading: boolean
  position: {top: number, left: number}
}>()

// Splits a name into before, match and after pieces so the template can bold the typed text. The match is
// found without regard to case, but each piece keeps the name's original casing.
const nameParts = (name: string): {text: string, isMatch: boolean}[] => {
  const start = props.typedText ? name.toLowerCase().indexOf(props.typedText.toLowerCase()) : -1
  if (start < 0) {
    return [{text: name, isMatch: false}]
  }
  const end = start + props.typedText.length
  return [
    {text: name.slice(0, start), isMatch: false},
    {text: name.slice(start, end), isMatch: true},
    {text: name.slice(end), isMatch: false}
  ].filter(part => part.text)
}

// Second line of an option: "title — department", leaving out whichever part is missing (and the dash with it).
const subtitle = (user: TaggableUser): string => compact([user.title, user.deptName]).join(' — ')
</script>

<style scoped>
.user-tag-dropdown {
  background-color: rgb(var(--v-theme-surface));
  border: 1px solid rgb(var(--v-theme-quaternary));
  border-radius: 0.25rem;
  box-shadow: 0 0.25rem 0.75rem rgba(0, 0, 0, 0.2);
  color: rgb(var(--v-theme-on-surface));
  list-style: none;
  margin: 0;
  max-width: 100%;
  overflow-wrap: anywhere;
  padding: 0.25rem 0;
  position: absolute;
  /* Above the editor content, below Vuetify overlays (which start at 2000). */
  z-index: 1000;
}
.user-tag-message {
  color: rgba(var(--v-theme-on-surface), 0.7);
  padding: 0.5rem 0.75rem;
}
.user-tag-option {
  cursor: pointer;
  min-height: 1.5rem;
  padding: 0.375rem 0.75rem;
}
.user-tag-option:hover {
  background-color: rgb(var(--v-theme-surface-light));
}
/* The outline is the non-color cue for the highlighted row; the background reinforces it. */
.user-tag-option-highlighted,
.user-tag-option-highlighted:hover {
  background-color: rgb(var(--v-theme-light-blue));
  outline: 2px solid rgb(var(--v-theme-quaternary));
  outline-offset: -2px;
}
/* Smaller and gray, so the name stands out. At 0.65 the text is about #595959 on white (7:1), and on the highlighted
   row's light blue (#c0ecff) it is still above the 4.5:1 AA minimum. */
.user-tag-subtitle {
  color: rgba(var(--v-theme-on-surface), 0.65);
  font-size: 0.75rem;
}
</style>
