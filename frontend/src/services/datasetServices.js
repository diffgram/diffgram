import axios from "@/services/customInstance";


export const get_dataset_list = async (project_string_id) => {
  try {
    const { data } = await axios.post(`/api/v1/project/${project_string_id}/directory/list`, {})
    let directory_list = data.directory_list;
    console.log('dasd', directory_list)
    for (let elm of directory_list){
      console.log(elm.nickname)
    }
    return [directory_list, null]
  } catch(e) {
    return [null, e]

  }
}
