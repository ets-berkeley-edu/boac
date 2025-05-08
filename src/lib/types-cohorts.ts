
export type Cohort = {
  domain: string,
  id: number,
  name: string,
  totalStudentCount: number
}

export type FilterCategories = Record<string, FilterOption[]>

export type FilterOption = {
  disabled: boolean,
  label: FilterOptionLabel,
  key: string
}

export type FilterOptionLabel = {
  primary: string
  range: string[],
  rangeMinEqualsMax: string
}
