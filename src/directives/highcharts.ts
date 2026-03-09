import {first, size} from 'lodash'
import {nextTick} from 'vue'
import type {ObjectDirective} from 'vue'
import type {ElWithObserver} from '@/lib/types'

export type HighchartsA11yDirective = ObjectDirective

declare module 'vue' {
  export interface ComponentCustomProperties {
    vHighchartsA11y: HighchartsA11yDirective
  }
}

const setSvgAttributes = (el: Element, chartDetails?: Element) => {
  const svg = first(el.getElementsByTagName('svg'))
  if (svg) {
    svg.setAttribute('role', 'application')
    if (chartDetails && size(chartDetails.getAttribute('id'))) {
      svg.setAttribute('aria-describedby', String(chartDetails.getAttribute('id')))
    }
  }
}

export default {
  mounted: (el: ElWithObserver) => {
    nextTick(() => {
      const chartDetails = first(el.querySelectorAll('[id^="highcharts-screen-reader-region-before"]'))
      const container = first(el.getElementsByClassName('highcharts-container'))
      const exitAnchor = first(el.getElementsByClassName('highcharts-exit-anchor'))

      // prevent screen reader text from being announced as 'clickable' due to the attached mousedown handler
      el.setAttribute('role', 'presentation')

      // avoid exposing presentational element to assistive technologies
      el.removeAttribute('aria-hidden')
      el.removeAttribute('aria-label')
      el.__observer = new MutationObserver((mutations) => {
        mutations.forEach(() => {
          if (el.getAttribute('aria-hidden') === 'false') {
            el.removeAttribute('aria-hidden')
          }
        })
      })
      el.__observer.observe(el, {attributes: true, attributeFilter: ['aria-hidden']})

      if (container) {
        // make keyboard navigation work with JAWS
        container.setAttribute('role', 'application')
      }
      if (exitAnchor) {
        exitAnchor.removeAttribute('tabindex')
      }
      setSvgAttributes(el, chartDetails)
    })
  },
  beforeUnmount: (el: ElWithObserver) => {
    el.__observer?.disconnect()
    delete el.__observer
  }
} satisfies HighchartsA11yDirective
