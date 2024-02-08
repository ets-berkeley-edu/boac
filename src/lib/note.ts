import store from '@/store'
import {each, isEmpty, size, trim} from 'lodash'

export function validateTemplateTitle(template: any) {
  const title = trim(template.title)
  let msg: string | undefined = undefined
  if (isEmpty(title)) {
    msg = 'Required'
  } else if (size(title) > 255) {
    msg = 'Name must be 255 characters or fewer'
  } else {
    const myTemplates = store.getters['note/noteTemplates']
    each(myTemplates, existing => {
      if (
        (!template.id || template.id !== existing.id) &&
        title.toUpperCase() === existing.title.toUpperCase()
      ) {
        msg = 'You have an existing template with this name. Please choose a different name.'
        return false
      }
    })
  }
  return msg
}
