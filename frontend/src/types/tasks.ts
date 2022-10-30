import { File } from "./files"
import { LabelSchema } from "./label"

export type Task = {
  id: number,
  job_id: number,
  file: File,
  job: Job
}

export type Job = {
  id: number,
  name: string,
  type: string,
  time_created: string,
  label_schema_id: number,
  allow_reviews: boolean,
  is_pinned: boolean,
  label_schema: LabelSchema
}