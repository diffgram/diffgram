

export type Sequence = {
  id: number,
  number: number,
  instance_preview: {
    id: number,
    file_id: number,
    preview_image_url: string
  },
  key_frame_list: {
    frame_number_list: number[]
  },
  label_file_id: number,
  single_frame: boolean

}
