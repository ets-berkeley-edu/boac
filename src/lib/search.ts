import {useContextStore} from '@/stores/context'
import {useSearchStore} from '@/stores/search'
import {oxfordJoin} from '@/lib/utils'

export function labelForSearchInput() {
  const currentUser = useContextStore().currentUser
  const scopes = ['students']
  if (currentUser.canAccessCanvasData) {
    scopes.push('courses')
  }
  if (currentUser.canAccessAdvisingData) {
    scopes.push('notes')
  }
  const history = useSearchStore().searchHistory
  return `Search for ${oxfordJoin(scopes)}.${history && history.length ? ' Expect auto-suggest of previous searches.' : ''}`
}
