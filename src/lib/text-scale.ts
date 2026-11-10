import {computed} from 'vue'
import type {ComputedRef} from 'vue'
import {useDisplay} from 'vuetify'

// The root font size that BOA's pixel breakpoints were designed around (the browser default).
const DESIGN_ROOT_FONT_SIZE = 16

const getRootFontSize = (): number => {
  const size = parseFloat(window.getComputedStyle(document.documentElement).fontSize)
  return size > 0 ? size : DESIGN_ROOT_FONT_SIZE
}

/**
 * Vuetify's breakpoints compare the viewport against fixed pixel values, so a user who raises the browser's
 * font size (e.g. to 200%) keeps getting wide, multi-column layouts that no longer fit their larger text.
 * This returns the viewport width scaled to the default font size: at 200% text, a 1600px window counts as
 * 800px. Compare it against a pixel breakpoint to decide when a layout should stack (WCAG 1.4.4 and 1.4.10).
 */
export function useTextScaledDisplayWidth(): ComputedRef<number> {
  const {width} = useDisplay()
  // The root font size is re-read whenever the viewport width changes, which keeps this cheap. A font-size
  // change with no resize takes effect on the next resize or page load.
  return computed(() => width.value * DESIGN_ROOT_FONT_SIZE / getRootFontSize())
}
