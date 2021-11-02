import Vuex from "vuex";
import axios from 'axios'
import { shallowMount, createLocalVue } from "@vue/test-utils";
import login from "@/components/user/login.vue";

const localVue = createLocalVue();
localVue.use(Vuex);
jest.mock('axios');

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

  it("It has to invoke axios get function on the creation", () => {
    shallowMount(login, {
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

    expect(axios.get).toHaveBeenCalled()
  })

  it("It should not include magic link option when Mailgun is not set", () => {
    const wrapper = shallowMount(login, {
      data: function() {
        return {
          mailgun: false,
          mode: "password"
        }
      },
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
    
    expect(wrapper.text().toLowerCase()).not.toContain("magic link")
  })

  it("It should include magic link option when Mailgun is set", () => {
    const wrapper = shallowMount(login, {
      data: function() {
        return {
          mailgun: true,
          mode: "magic_auth"
        }
      },
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
    
    expect(wrapper.text().toLowerCase()).toContain("magic link")
  })

});
