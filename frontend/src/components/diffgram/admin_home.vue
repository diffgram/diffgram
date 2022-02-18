<template>
  <div>

    <project_manager :mode="'super_admin'"> </project_manager>


  </div>
</template>

<script lang="ts">

import project_manager from '../project/project_manager'

import Vue from "vue"; export default Vue.extend( {
  name: 'admin_home',
  components: {
    project_manager
  },
  props: [''],
  data() {
    return {


    }
  },
  mounted() {


  },
  methods: {

  }
}

) </script>
