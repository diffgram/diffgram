import testUser from '../../../fixtures/users.json';

describe('UI Schema', () => {

  context('Setup', () => {
    before(function () {
      cy.loginByForm(testUser.email, testUser.password);
    })
    context('UI Schema', () => {

      it('Creates New', () => {

        cy.visit(`http://localhost:8085/task/1/?edit_schema=true`);

        cy.get('[data-cy="ui_schema_new"]').click({force: true})
        cy.wait(1000)

      })

      it('Hides Home Button', () => {
        cy.get('[data-cy="toolbar_home_button"]').trigger('mouseover')
        cy.wait(400)

        cy.get('[data-cy="hide_target_element"]').click({force: true})
        cy.wait(400)

        // Triggers mouse move away
        cy.get('[data-cy="toolbar_zoom_info"]').trigger('mouseover')
        cy.wait(400)

        const getStore = () => cy.window().its('app.$store')

        getStore().its('state.ui_schema.current.home.visible').should('eq', false);

      })

      it('Restores Settings', () => {
        cy.get('[data-cy="reset_defaults"]').click({force: true})
        cy.wait(2000)

        const getStore = () => cy.window().its('app.$store')
        getStore().its('state.ui_schema.current.home.visible').should('eq', true);

      })

      it("Works to be able to hide after cycling show/hide", () => {

        // Try to hover over it again
        cy.get('[data-cy="toolbar_home_button"]').trigger('mouseover')
        cy.wait(400)

        cy.get('[data-cy="hide_target_element"]').click({force: true})
        cy.wait(400)

      })

      it("Saves", () => {
        cy.get('[data-cy="ui_schema_save"]').click({force: true})

      })
    })
  })
})
