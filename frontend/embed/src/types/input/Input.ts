import InstanceList from "../helpers/instance_list";

export type FramePacketMap ={
  [key: number]: InstanceList
}
export type Media = {
  url: string
  type: string
}
export type Input = {
  id?: number,
  media: Media,
  frame_packet_map: FramePacketMap,
  type: string
  connection_id?: number,
  parent_file_id?: number,
  directory_id: number,
  original_filename: number,
  bucket_name?: string
  raw_data_blob_path?: string
  instance_list?: InstanceList
  job_id?: number
  video_split_duration?: number
}
