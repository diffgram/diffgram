import { shallowMount, createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";
import login from "@/components/user/login.vue";

const localVue = createLocalVue();

localVue.use(Vuex);

describe("footer.vue", () => {
  it("Render footer component", () => {
    const wrapper = shallowMount(login, {
      mocks: {
        $store: {
          state: {
            user: {
              logged_in: false
            }
          }
        }
      },
      localVue
    });
  });
});
