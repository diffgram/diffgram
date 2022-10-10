<template>
    <v-card elevation="0">
      <v-container>
        <v-layout column>
          <v-card-title>
            New Dataset
          </v-card-title>

          <v-text-field 
            label="Name"
            v-model="nickname"
          />

          <v-btn 
            @click="new_directory"
            :loading="loading"
            :disabled="loading"
            color="primary"
          >
            Create
          </v-btn>

          <div class="text-xs-left pt-4">
            <v-btn 
              dark
              outlined
              color="primary"
              href="https://diffgram.readme.io/docs/data-directories-introduction"
              target="_blank"
            >
              Help
              <v-icon right>
                mdi-book
              </v-icon>
            </v-btn>
          </div>

          <v_error_multiple :error="error" />

          <v-alert 
            v-if="show_success"
            type="success"
          >
            Created.
          </v-alert>
        </v-layout>
      </v-container>
    </v-card>
</template>

<script lang="ts">
import Vue from "vue"; 
import sillyname from 'sillyname';
import { create_new_dataset } from "../../../services/datasetServices";

export default Vue.extend( {
  name: 'dataset_new',
  props: {
    project_string_id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      mode: "user" as string,
      loading: false as boolean,
      show_success: false as boolean,
      error: {} as object,
      nickname: sillyname().split(" ")[0] as string,
    }
  },
  methods: {
    new_directory: async function (): Promise<void> {
      this.loading = true
      this.error = {}
      this.show_success = false

      const [success, error] = await create_new_dataset(this.project_string_id, this.nickname)

      if (!error) {
        this.show_success = true
        this.$emit('directory_created', success.new_directory)
      } else {
        this.error = error.response.data.log.error
      }

      this.loading = false
    }

  }
}
) 
</script>
