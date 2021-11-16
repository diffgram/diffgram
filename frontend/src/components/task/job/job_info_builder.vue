<template>
  <div v-cloak>
    <div v-if="['job_edit'].includes(mode_view)">
      {{ job.status }}
    </div>

    <div v-if="job.td_api_trainer_basic_training == true">
      <h2><v-icon>mdi-heart</v-icon> Basic Training</h2>
    </div>
  </div>
</template>


<script lang="ts">
import axios from "axios";

import Vue from "vue";

export default Vue.extend({
  name: "job_overview_and_task_list",
  components: {},
  props: {
    job_id: {
      default: null,
    },
    mode_data: {
      default: null, // job_edit, job_detail
    },
    // not clear on difference between use for view and data in this context yet
    mode_view: {
      default: null, // job_edit, job_detail
    },
  },
  data() {
    return {
      loading: false,

      info: {},
      error: {},

      job: {
        percent_completed: 0,
        label_dict: null,
      },
    };
  },
  computed: {},

  watch: {},

  created() {
    this.job_builder_info();
  },
  methods: {
    job_builder_info: function () {
      this.loading = true;

      axios
        .post("/api/v1/job/" + this.job_id + "/builder/info", {
          mode_data: this.mode_data,
        })
        .then((response) => {
          if (response.data.log.success == true) {
            this.job = response.data.job;
            this.$emit("job_info", this.job);
            this.$store.commit("set_job", this.job);
          }

          this.loading = false;
        })
        .catch((error) => {
          if (error.response.status == 403) {
            this.$store.commit("error_permission");
          }

          console.error(error);
          this.loading = false;
        });
    },
  },
});
</script>
