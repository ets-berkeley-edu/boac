import {first} from 'lodash'
import {nextTick} from 'vue'
import type {Directive} from 'vue'

export type HighchartsA11yDirective = Directive<HTMLElement>

declare module 'vue' {
  export interface ComponentCustomProperties {
    vHighchartsA11y: HighchartsA11yDirective
  }
}

export default (el => {
  nextTick(() => {
    const svg = first(el.getElementsByTagName('svg'))
    if (svg) {
      svg.setAttribute('role', 'application')
    }
  })
}) satisfies HighchartsA11yDirective
