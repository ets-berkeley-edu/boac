import axios from 'axios';
import store from '@/store';

export function translateToMenu(filterCriteria: any) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/menu/cohort/translate_filter_criteria_to_menu`, {
      filterCriteria: filterCriteria
    })
    .then(response => response.data, () => null);
}

export function getCohortFilterOptions(existingFilters: any[]) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/menu/cohort/all_filter_options`, {
      existingFilters: existingFilters
    })
    .then(response => response.data, () => null);
}
