import _ from 'lodash'

export function oxfordJoin(arr, zeroString) {
  switch((arr || []).length) {
  case 0: return _.isNil(zeroString) ? '' : zeroString
  case 1: return _.head(arr)
  case 2: return `${_.head(arr)} and ${_.last(arr)}`
  default: return _.join(_.concat(_.initial(arr), `and ${_.last(arr)}`), ', ')
  }
}

