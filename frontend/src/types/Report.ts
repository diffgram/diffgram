import { ReportTemplate } from './ReportTemplate'
import { Schema } from './Schema'

export class Report {
  reportTemplate: ReportTemplate = null
  schema: Schema = new Schema()
  count: number = null
  labels: string[] = null
  second_grouping: number[] = null
  values: number[] = null
  values_metadata: number[] = null
}

