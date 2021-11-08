<template>
  <v-container class="grey lighten-5">
    <v-btn @click="change_stats_visibility" text
      >{{ stats_visibility ? "Hide" : "Show job" }} satistics</v-btn
    >
    <v-row v-if="stats_visibility">
      <v-col cols="12" sm="4">
        <v-card
          style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
          "
          class="mx-auto"
          height="250px"
          max-width="100%"
          outlined
        >
          <h3>Job progress:</h3>
          <div v-if="job_data_fetched" style="width: 50%">
            <pie-chart
              :data="job_chart.chartData"
              :options="job_chart.chartOptions"
            ></pie-chart>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="4">
        <v-card
          style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
          "
          class="mx-auto"
          height="250px"
          max-width="100%"
          outlined
        >
          <h3>My progress:</h3>
          <br />
          <br />
          <div v-if="job_data_fetched" style="width: 80%">
            <span style="display: flex; justify-content: space-between">
              Total tasks assigned:
              <strong>{{ current_user_performance.total }}</strong>
            </span>
            <br />
            <span style="display: flex; justify-content: space-between">
              Tasks completed:
              <strong>{{ current_user_performance.completed }}</strong>
            </span>
            <br />
            <span style="display: flex; justify-content: space-between">
              Annotations created:
              <strong>{{ current_user_performance.instances }}</strong>
            </span>
            <br />
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="4">
        <v-card
          style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
          "
          class="mx-auto"
          height="250px"
          max-width="100%"
          outlined
        >
          <v-menu offset-y>
            <template v-slot:activator="{ on, attrs }">
              <div v-if="!update_user_cart && job_data_fetched">
                <v-avatar size="30" v-bind="attrs" v-on="on" color="indigo">
                  <v-icon dark> mdi-account-circle </v-icon>
                </v-avatar>
                <span v-on="on" style="cursor: pointer">
                  {{
                    member_list.find((item) => item.id === show_member_stat)
                      .first_name
                  }}
                  {{
                    member_list.find((item) => item.id === show_member_stat)
                      .last_name
                  }}
                </span>
                <v-icon> arrow_drop_down </v-icon>
              </div>
              <div v-else>
                <span v-on="on" style="cursor: pointer">
                  Getting data for
                  {{
                    member_list.find((item) => item.id === show_member_stat)
                      .first_name
                  }}
                  ...
                </span>
              </div>
            </template>
            <v-list>
              <v-list-item v-for="(member, index) in member_list" :key="index">
                <v-list-item-title
                  style="cursor: pointer"
                  @click="
                    () => {
                      show_member_stat = member.id;
                      update_user_cart = true;
                    }
                  "
                >
                  <v-avatar size="30" v-bind="attrs" v-on="on" color="indigo">
                    <v-icon dark> mdi-account-circle </v-icon>
                  </v-avatar>
                  {{ member.first_name }} {{ member.last_name }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
          <div v-if="!update_user_cart && job_data_fetched" style="width: 50%">
            <pie-chart
              :data="user_stats.chartData"
              :options="user_stats.chartOptions"
            />
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Vue from "vue";
import pieChart from "../report/charts/pieChart";
import store from "../../store";
import {
  getJobStats,
  getJobStatsForUser,
} from "../../services/jobStatsServices";

export default Vue.extend({
  components: {
    pieChart,
  },
  store,
  watch: {
    update_user_cart: {
      async handler(value) {
        if (value) {
          const { job_id } = this.$route.params;
          const userStats = await getJobStatsForUser(
            job_id,
            this.show_member_stat
          );
          this.user_stats.chartData.datasets[0].data = [
            userStats.completed,
            userStats.total - userStats.completed,
          ];
          this.update_user_cart = false;
        }
      },
    },
  },
  methods: {
    change_stats_visibility() {
      this.stats_visibility = !this.stats_visibility;
      localStorage.setItem("diff_stats_task_visibility", this.stats_visibility);
    },
  },
  async created() {
    const stats_visibility_status = localStorage.getItem(
      "diff_stats_task_visibility"
    );

    const user_id = this.$store.state.user.current.id;
    const { job_id } = this.$route.params;

    const member_list = [...this.$store.state.project.current.member_list];
    this.member_list = member_list;
    this.show_member_stat = user_id;

    const { completed, total } = await getJobStats(job_id);
    const userStats = await getJobStatsForUser(job_id, user_id);
    this.current_user_performance = {
      instances: userStats.instaces_created,
      total: userStats.total,
      completed: userStats.completed,
    };
    this.job_chart.chartData.datasets[0].data = [completed, total - completed];
    this.user_stats.chartData.datasets[0].data = [
      userStats.completed,
      userStats.total - userStats.completed,
    ];
    this.job_data_fetched = true;

    if (stats_visibility_status)
      this.stats_visibility = JSON.parse(stats_visibility_status);
  },
  data() {
    return {
      stats_visibility: true,
      current_user_stat: "two",
      update_user_cart: false,
      job_data_fetched: false,
      show_member_stat: null,
      current_user_performance: {
        instances: 0,
        total: 0,
        completed: 0,
      },
      job_chart: {
        chartOptions: {
          hoverBorderWidth: 20,
        },
        chartData: {
          hoverBackgroundColor: "red",
          hoverBorderWidth: 10,
          labels: ["Completed", "Pending"],
          datasets: [
            {
              label: "Data One",
              backgroundColor: ["#41B883", "#00D8FF"],
              data: [],
            },
          ],
        },
      },
      user_stats: {
        chartOptions: {
          hoverBorderWidth: 20,
        },
        chartData: {
          hoverBackgroundColor: "red",
          hoverBorderWidth: 10,
          labels: ["Completed", "Pending"],
          datasets: [
            {
              label: "Data One",
              backgroundColor: ["#41B883", "#E46651"],
              data: [],
            },
          ],
        },
      },
    };
  },
});
</script>