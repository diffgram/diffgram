import sillyname from "sillyname";

export const create_empty_job = () => {
  return {
    name: sillyname().split(" ")[0],
    label_mode: "closed_all_available",

    loading: false,
    passes_per_file: 1,
    share_object: {
      // TODO this may fail for org jobs? double check this.
      text: String,
      type: "project",
    },
    share: "project",
    allow_reviews: false,
    review_chance: 0,
    label_schema_id: undefined,
    label_schema: undefined,
    instance_type: "box", //"box" or "polygon" or... "text"...
    permission: "all_secure_users",
    field: "Other",
    category: "visual",
    attached_directories_dict: { attached_directories_list: [] },
    type: "Normal",
    connector_data: {},
    // default to no review while improving review system
    review_by_human_freqeuncy: "No review", //'every_3rd_pass'
    td_api_trainer_basic_training: false,
    file_handling: "use_existing",
    interface_connection: undefined,
    member_list_ids: ["all"],
    reviewer_list_ids: ["all"],
  }
}


export default create_empty_job
