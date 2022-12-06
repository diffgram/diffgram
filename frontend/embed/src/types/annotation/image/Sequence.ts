

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


var seq_color_map = [
  "blue",
  "green",
  "pink",
  "orange",
  "red",
  "purple",
  "indigo",
  "cyan",
  "teal",
  "orange"
]

export function get_sequence_color (number: number | string) {

  if (number) {
      return seq_color_map[(parseInt(number as string) % 10)]
  }

  return "black"

  /* Where mod number is related to length of color map
    * This makes it work with overflow (instead of just grabbing it directly)
    *
    * careful with () vs [] notation for methods vs access
    * in vue js
    * could also think about allowing this to be user set
    */

}
