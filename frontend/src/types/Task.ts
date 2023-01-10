export type Task = {
  id: number
  is_live: boolean
  is_root: boolean
  parent_id: boolean
  child_primary_id: boolean
  job_id: number
  kind: string
  task_type: string
  job_type: string
  status: string
  file_original_id: number
  file_id: number
  completion_directory_id: number
  incoming_directory_id: number
  completion_action: string
  guide_id: number
  project_id: number

  label_mode: string
  label_dict: object
  text_tokenizer: string
  gold_standard_file: object
  assignee_user_id: number
  previous_assignees: number[]
  time_created: Date
  time_completed: Date
  time_updated: Date
  count_instances_chagned: number
  reviewed_no_changes: boolean
  review_star_rating_average: number
  gold_standard_missing: number
  default_external_map_id: number
}
