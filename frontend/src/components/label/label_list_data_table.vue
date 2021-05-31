<template>
<div v-cloak>

<v-spacer></v-spacer>
<v-text-field v-model="search"
              append-icon="search"
              label="Search"
              single-line
              hide-details></v-text-field>
<v-spacer></v-spacer>


 <!-- CAUTION this component does not emit anything yet -->

<v-data-table :headers="header_list"
              :items="label_list"
              :search="search"
              v-model="selected"
              class="elevation-1"
              item-key="id"
              ref="label_data_table"
              >

  <!-- appears to have to be item for vuetify syntax-->
  <template slot="item" slot-scope="props">

  <tr>
      <td>
        <v-checkbox v-model="props.isSelected"
                    @change="props.select($event)"
                    primary>
        </v-checkbox>
      </td>

      <td>

        <div v-if="props.item.colour != undefined">
          <v-icon :style="style_color(props.item.colour.hex)"
                  class="clickable"
                  @click="change_label_function(props.item)"
                  >flag</v-icon>
        </div>

      </td>

      <td>
        {{ props.item.label.name }}
      </td>
    </tr>

  </template>

  <v-alert slot="no-results"  color="error" icon="warning">
    Your search for "{{ search }}" found no results.
  </v-alert>

</v-data-table>



</div>
</template>

<script lang="ts">

import axios from 'axios';

  import Vue from "vue"; export default Vue.extend( {
    name: 'label_list_data_table',

    props: {
      'project_string_id': {},
      'view_only_mode': {}
      },
  watch: {

  },
  mounted() {

   this.refresh_label_list()

  },
  data() {
    return {

      search: null,

      label_list : [],

      selected : [],  // would prefer selected_list but vuetify seems to need 'selected'

      header_list: [
        {
          text: "Selected",
          align: 'left',
          value: 'selected'
        },
        {
          text: "Color",
          align: 'left',
          sortable: false,
          value: 'label.colour'
        },
        {
          text: "Name",
          align: 'left',
          value: "label.name"
        }
      ]

    }
  },

  methods: {

    refresh_label_list: function () {

      if (this.project_string_id == null) {
        return
      }

      var url = null
      this.label_refresh_loading = true

      url = '/api/project/' + this.project_string_id + '/labels/refresh'

      axios.get(url, {})
      .then(response => {

        this.label_list = response.data.labels_out

      })
      .catch(error => {
        console.error(error);
      });

    },

    style_color: function (hex) {
      return "color:" + hex
    }

  }
}

) </script>
