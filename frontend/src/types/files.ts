export type File = {
  id: number,
  original_filename: string,
  type: string,
  parent_id: number,
  hash: string
  state: string
  created_time: Date,
  time_last_updated: Date,
  ann_is_complete: boolean,
  video_id?: number,
  video_parent_file_id?: number
  count_instances_changed: number
  image?: Image
  video?: Video
  text?: Text
  geospatial?: Geospatial
  audio?: Audio
  sensor_fusion?: SensorFusion

  row?: number

  column?: number
}
export type Video = {
  id: number
  filename: string
  frame_rate: number
  frame_count: number
  created_time: Date
  status: string
  description: string
  preview_image_url_thumb?: string
  file_blob_path: string
  file_signed_url?: string
  width: number
  height: number
  fps_conversion_ratio: number
  offset_in_seconds: number
  parent_video_split_duration: number
}

export type Image = {
  id: number
  original_filename: string
  width: number
  height: number
  rotation_degrees: number
  soft_delete: boolean
  url_signed?: string
  url_signed_thumb?: string
  url_signed_blob_path: string
  annotation_status: string
}

export type Text = {
  id: number
  original_filename: string
  soft_delete: boolean
  url_signed?: string
  url_signed_blob_path: string
  is_inference: boolean
  tokens_url_signed: string
  is_annotation_example: boolean
  annotation_status: string
}

export type Geospatial = {
  id: number
  original_filename: string
  description: string
  soft_delete: boolean
  file_id: number
  url_signed?: string
  url_signed_blob_path: string
  url_signed_expiry_force_refresh: number
  time_created: Date
  time_updated: Date
}

export type Audio = {
  id: number
  original_filename: string
  description: string
  soft_delete: boolean
  url_public?: string
  url_signed?: string
  url_signed_blob_path: string
  url_signed_expiry: number
  time_created: Date
  time_updated: Date
}

export type SensorFusion = {
  point_cloud: PointCloud
}

export type PointCloud = {
  id: number
  original_filename: string
  description: string
  soft_delete: boolean
  url_public?: string
  url_signed?: string
  url_signed_blob_path: string
  url_signed_expiry: number
  url_signed_expiry_force_refresh: number
  time_created: Date
  time_updated: Date
}
