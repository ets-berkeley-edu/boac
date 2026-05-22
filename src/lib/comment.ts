import {includes} from 'lodash'

export function isExternalCommentParent(parentType: string): boolean {
  return includes(['appointment', 'eForm'], parentType)
}
