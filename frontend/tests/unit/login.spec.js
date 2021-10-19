import Vuex from "vuex";
import { shallowMount, createLocalVue } from "@vue/test-utils";
import login from "@/components/user/login.vue";

const localVue = createLocalVue();
localVue.use(Vuex);

describe("login.vue", () => {
  it("Rendered login page has form component", () => {
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
    const hasForm = wrapper.find("form");
    expect(hasForm.html()).toBeTruthy();
  });
});
