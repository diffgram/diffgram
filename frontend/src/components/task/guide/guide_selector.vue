<template>
  <diffgram_select
    :item_list="guide_list"
    :return_object="true"
    value="id"
    name_key="name"
    @change="on_guide_change"
  >

  </diffgram_select>
</template>

<script lang="ts">

  import axios from '../../../services/customAxiosInstance';

  import Vue from "vue";

  export default Vue.extend({
      name: 'guide_selector',
      props: {
        'project_string_id': {
          default: null
        }
      },

      data() {
        return {

          my_stuff_only: false,

          guide_list: [],
        }
      },
      computed: {
        metadata: function () {

          return {
            'my_stuff_only': this.my_stuff_only,
            'limit': 1000,
            'request_next_page': false,
          }

        }
      },
      mounted() {
        this.guide_list_api()

      },
      methods: {
        on_guide_change: function(guide){
          this.$emit('change', guide)
        },
        guide_list_api: async function () {

          // there were some issues with how the
          // project string gets setup from the url (because the url doesn't contain the id),
          // so just use this from Store for now
          try {
            const response = await axios.post(
              `/api/v1/project/${this.$store.state.project.current.project_string_id}/guide/list`, {
                'metadata': this.metadata

              })

            if (response.data.log.success == true) {

              this.guide_list = response.data.guide_list
              this.metadata_previous = response.data.metadata
            }
          } catch (e) {
            console.error(e);
            this.loading = false

          }


        },

      }
    }
  ) </script>
