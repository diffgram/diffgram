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
          <div style="width: 50%">
            <pie-chart :data="chartData" :options="chartOptions"></pie-chart>
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
          <div style="width: 80%">
            <span style="display: flex; justify-content: space-between">
              Tasks completed:
              <strong>20</strong>
            </span>
            <br />
            <span style="display: flex; justify-content: space-between">
              Annotations created:
              <strong>42</strong>
            </span>
            <br />
            <span style="display: flex; justify-content: space-between">
              Avarage time per task:
              <strong>10 min</strong>
            </span>
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
              <div v-if="!update_user_cart">
                <v-avatar size="30" v-bind="attrs" v-on="on" color="indigo">
                  <v-icon dark> mdi-account-circle </v-icon>
                </v-avatar>
                <span v-on="on" style="cursor: pointer">
                  {{
                    items.find((item) => item.id === current_user_stat).title
                  }}
                </span>
              </div>
              <div v-else>
                <span v-on="on" style="cursor: pointer">
                  Getting data for
                  {{
                    items.find((item) => item.id === current_user_stat).title
                  }}
                  ...
                </span>
              </div>
            </template>
            <v-list>
              <v-list-item v-for="(item, index) in items" :key="index">
                <v-list-item-title
                  style="cursor: pointer"
                  @click="
                    () => {
                      current_user_stat = item.id;
                      update_user_cart = true;
                    }
                  "
                >
                  <v-avatar size="30" v-bind="attrs" v-on="on" color="indigo">
                    <v-icon dark> mdi-account-circle </v-icon>
                  </v-avatar>
                  {{ item.title }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
          <div style="width: 50%">
            <pie-chart
              v-if="!update_user_cart"
              :data="user_stats[current_user_stat].chartData2"
              :options="user_stats[current_user_stat].chartOptions2"
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
export default Vue.extend({
  components: {
    pieChart,
  },
  watch: {
    update_user_cart: {
      handler(value) {
        if (value) setTimeout(() => (this.update_user_cart = false), 2000);
      },
    },
  },
  methods: {
    change_stats_visibility() {
      this.stats_visibility = !this.stats_visibility;
      localStorage.setItem("diff_stats_task_visibility", this.stats_visibility);
    },
  },
  created() {
    const stats_visibility_status = localStorage.getItem(
      "diff_stats_task_visibility"
    );

    if (stats_visibility_status)
      this.stats_visibility = JSON.parse(stats_visibility_status);
  },
  data() {
    return {
      stats_visibility: true,
      current_user_stat: "two",
      update_user_cart: false,
      chartOptions: {
        hoverBorderWidth: 20,
      },
      chartData: {
        hoverBackgroundColor: "red",
        hoverBorderWidth: 10,
        labels: ["Completed", "QA", "Un done"],
        datasets: [
          {
            label: "Data One",
            backgroundColor: ["#41B883", "#E46651", "#00D8FF"],
            data: [1, 3, 2],
          },
        ],
      },
      user_stats: {
        one: {
          chartOptions2: {
            hoverBorderWidth: 20,
          },
          chartData2: {
            hoverBackgroundColor: "red",
            hoverBorderWidth: 10,
            labels: ["Completed", "QA", "Un done"],
            datasets: [
              {
                label: "Data One",
                backgroundColor: ["#41B883", "#E46651", "#00D8FF"],
                data: [2, 4, 3],
              },
            ],
          },
        },
        two: {
          chartOptions2: {
            hoverBorderWidth: 20,
          },
          chartData2: {
            hoverBackgroundColor: "red",
            hoverBorderWidth: 10,
            labels: ["Completed", "QA", "Un done"],
            datasets: [
              {
                label: "Data One",
                backgroundColor: ["#41B883", "#E46651", "#00D8FF"],
                data: [4, 4, 4],
              },
            ],
          },
        },
        three: {
          chartOptions2: {
            hoverBorderWidth: 20,
          },
          chartData2: {
            hoverBackgroundColor: "red",
            hoverBorderWidth: 10,
            labels: ["Completed", "QA", "Un done"],
            datasets: [
              {
                label: "Data One",
                backgroundColor: ["#41B883", "#E46651", "#00D8FF"],
                data: [1, 3, 2],
              },
            ],
          },
        },
      },
      items: [
        { title: "Anthony Sarkis", id: "one" },
        { title: "Pablo Estrada", id: "two" },
        { title: "Vitalii Buyzhyn", id: "three" },
      ],
    };
  },
});
</script>