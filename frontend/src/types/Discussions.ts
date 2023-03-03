
export type DiscussionMember = {
  id: number,
  user_id: number,
  discussion_id: number
  project_id: number,
  content: string,
  member_created_id: number,
  member_updated_id: number,
  time_created: Date,
  time_updated: Date
}

export type DiscussionComment = {
  id: number,
  user_id: number,
  discussion_id: number
}
export type Discussion = {
  id: number,
  created_time: Date,
  title: string,
  description: string,
  member_created_id: number,
  project_id: number,
  status: string
  type: string,
  assignees: DiscussionMember[],
  comment_list: DiscussionComment[],
  marker_type: string,
  marker_data: any,
  marker_frame_number: number
}
