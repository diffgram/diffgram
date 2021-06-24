<template>

  <v-container fluid style="background: white">
    <v-container v-if="!loading">
      <h3>Let's build your query! </h3>
      <h4 v-if="type === 'entities'">What do you want to filter?</h4>
      <h4 v-if="type === 'text'">Select an entity: </h4>
      <h4 v-if="type === 'boolean_operator'">Do you want to add more conditions?: </h4>
      <h4
        v-if="type === 'labels'">
        Select a label to filter by:
      </h4>
      <v-container fluid class="d-flex flex-wrap">
        <div v-if="['labels'].includes(type)" >
          <v-btn small
                 class="ma-1"
                 v-for="(item, index) in suggestions"
                 @click="update_query(`${transform_value(item)} `)">
            {{item}}
          </v-btn>
        </div>
        <div v-else-if="['entities', 'text'].includes(type)">

          <v-btn small
                 class="ma-1"
                 v-for="(item, index) in suggestions"
                 @click="update_query(`${transform_value(item)}.`)">
            {{item}}
          </v-btn>
          <h4 class="mt-4" v-if="type === 'text'">Or input a value: </h4>
          <div class="d-flex align-center justify-start" style="max-width: 50%">
            <v-text-field v-if="type === 'text'" v-model="filter_num"></v-text-field>
            <v-btn v-if="type === 'text'"
                   small
                   color="secondary"
                   @click="update_query(filter_num.toString() + ' ')">
              Set
            </v-btn>
          </div>
        </div>
        <div v-else-if="['boolean_operator'].includes(type)">

          <v-btn small
                 class="ma-1"
                 @click="update_query(`or `)">
            Expand My Selection
          </v-btn>
          <v-btn small
                 class="ma-1"
                 @click="update_query(`and `)">
            Narrow Down My Selection
          </v-btn>

        </div>
        <div v-else-if="type === 'operator'" class="d-flex justify-start align-center">
          <h4 v-if="item === ''">Select an operator: </h4>
          <v-btn class="ma-1" small @click="update_query(` > `)"> ></v-btn>
          <v-btn class="ma-1" small @click="update_query(` < `)"> <</v-btn>
          <v-btn class="ma-1" small @click="update_query(` >= `)"> >=</v-btn>
          <v-btn class="ma-1" small @click="update_query(` = `)"> =</v-btn>
          <v-btn class="ma-1" small @click="update_query(` != `)"> !=</v-btn>
        </div>

        <div v-else-if="type === 'text'" class="d-flex justify-start align-center">
          <h4>Please input a value: </h4>

        </div>

      </v-container>
      <div class="d-flex justify-end">

        <v-btn data-cy="execute_query_button" color="success" class="text-right" @click="execute_query">Execute</v-btn>
      </div>
    </v-container>
    <v-progress-circular indeterminate v-else></v-progress-circular>
  </v-container>


</template>

<script lang="ts">

  // TODO combine directory list elements into single component
  // look at props for passing some of stuff...

  // TODO pass loading or?

  import axios from 'axios';
  import v_new_directory from './directory_new'
  import v_update_directory from './directory_update'
  import Vue from "vue";

  export default Vue.extend({
    name: 'query_suggestion_menu',
    props: {
      'project_string_id': {
        default: null
      },
      'query': {
        default: null
      },
    },
    components: {},
    data() {
      return {
        is_open: false,
        filter_num: 1,
        suggestions: [],
        type: 'entities',
        compare_ops: ['=', '!=', '>', '<', '>=', '<='],
        state_id: 0,
        loading: false
      }
    },
    created() {

    },
    mounted() {
      this.get_query_suggestions();
    },
    watch: {
      query: async function () {
        await this.get_query_suggestions();
      }
    },
    methods: {
      transform_value(query_val) {
        return query_val.replaceAll(' ', '_')
      },
      execute_query: function(){
        this.$emit('execute_query', this.$props.query)
      },
      update_query: function (value) {
        this.$emit('update_query', value)
      },
      ends_with_multiple(s, arr){
        for (const elm of arr){
          if (s.endsWith(elm)){
            return true
          }
        }
        return false
      },
      async get_query_suggestions(event) {
        let query_val = ''
        if (!this.$props.query) {
          query_val = ''
        } else {
          query_val = this.$props.query;
        }
        if (query_val !== '' && !query_val.endsWith('.') && this.ends_with_multiple(query_val, this.compare_ops)) {
          query_val = query_val + '.'
        }
        this.loading = true
        try {
          const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/query-suggest`, {
            query: query_val
          })
          if (response.data && response.status === 200) {
            this.suggestions = response.data.suggestions;
            this.type = response.data.type;
            this.state_id = response.data.state_id;
          }
        } catch (error) {
          console.error(error);
        } finally {
          this.loading = false
        }
      },

    },
    beforeDestroy() {

    }
  })
</script>


<style scoped>

  .v-list {
    height: 500px;
    overflow-y: auto
  }

</style>
