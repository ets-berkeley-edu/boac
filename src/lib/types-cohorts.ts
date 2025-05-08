
export type Cohort = {
  domain: string,
  id: number,
  name: string,
  totalStudentCount: number
}

export type FilterOptionGroup = Record<string, FilterOption[]>

export type FilterOption = {
  disabled: boolean,
  label: FilterOptionLabel,
  key: string,
  name: string,
  value: object
}

export type FilterOptionLabel = {
  primary: string
  range: string[],
  rangeMinEqualsMax: string
}
