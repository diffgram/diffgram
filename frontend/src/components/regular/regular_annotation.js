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

export function get_sequence_color (number) {

  if (number) {
      return seq_color_map[(parseInt(number) % 10)]
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
