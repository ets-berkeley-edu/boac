import axios from 'axios';
import utils from '@/api/api-utils';

export function translateToMenu(criteria: any) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/menu/cohort/translate_filter_criteria_to_menu`, { criteria: criteria })
    .then(response => response.data, () => null);
}

export function getCohortFilterOptions(existingFilters: any[]) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/menu/cohort/all_filter_options`, {
      existingFilters: existingFilters
    })
    .then(response => response.data, () => null);
}
