import {first, size} from 'lodash'
import {nextTick} from 'vue'
import type {Directive} from 'vue'

export type HighchartsA11yDirective = Directive<HTMLElement>

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

export default ((el: Element) => {
  nextTick(() => {
    const chartDetails = first(el.querySelectorAll('[id^="highcharts-screen-reader-region-before"]'))
    const container = first(el.getElementsByClassName('highcharts-container'))
    if (container) {
      // make keyboard navigation work with JAWS
      container.setAttribute('role', 'application')
    }
    setSvgAttributes(el, chartDetails)
  })
}) satisfies HighchartsA11yDirective
