import {BoaUser, oxfordJoin} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useSearchStore} from '@/stores/search'

export function labelForSearchInput() {
  const currentUser: BoaUser = useContextStore().currentUser
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
