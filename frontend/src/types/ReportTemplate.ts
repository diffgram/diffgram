

export type ReportTemplate = {
  name: string,
  archived: boolean,
  item_of_interest: string,
  period: string,
  date_period_unit: string,
  label_file_id_list: number[],
  group_by: string,
  second_group_by: string,
  directory_id_list: number[],
  scope: string,
  view_type: string,
  diffgram_wide_default: boolean,
  id: number,
  view_sub_type: string
  task_event_type: string
}
