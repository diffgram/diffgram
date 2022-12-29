import { ReportTemplate } from './ReportTemplate'
import { Schema } from './Schema'

export type Report = {
  reportTemplate: ReportTemplate,
  schema: Schema,
  count: number,
  labels: string[],
  second_grouping: number[],
  values: number[],
  values_metadata: number[]
}

