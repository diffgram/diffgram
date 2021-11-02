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

  it("Displays 'Already Logged In.' message to logged in users", () => {
    const message = "Already Logged In.";
    const wrapper = shallowMount(login, {
      mocks: {
        $store: {
          state: {
            user: {
              logged_in: true
            }
          }
        }
      },
      localVue
    });
    const showedMessage = wrapper.text();
    expect(showedMessage).toMatch(message);
  });

});
