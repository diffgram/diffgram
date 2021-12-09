<template>
  <div>

    <v_account_info @account="account = $event">

    </v_account_info>


    <v_report_transactions :account="account">

    </v_report_transactions>

    <v_transaction_list :account="account">

    </v_transaction_list>


  </div>
</template>

<script lang="ts">


import axios from 'axios';


import Vue from "vue"; export default Vue.extend( {
  name: 'account_overview',
  props: [''],
  data() {
    return {

      account: {
        id: null
      },

      loading: false,
      errors: null,

    }
  },
  mounted() {


  },
  methods: {

  }
}

) </script>
