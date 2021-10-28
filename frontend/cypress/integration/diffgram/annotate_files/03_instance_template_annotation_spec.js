import testUser from '../../../fixtures/users.json';
import labelsForAttributes from '../../../fixtures/labelsForAttributes.json';
import testLabels from "../../../fixtures/labels.json";


describe('Instance Template Annotation', () => {

  context('Draws an Instance Template', () => {
  
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({preserve: ['session']})
        
      cy.loginByForm(testUser.email, testUser.password);
      cy.gotToProject(testUser.project_string_id);
      cy.createLabels(testLabels)
      cy.uploadAndViewSampleImage(testUser.project_string_id);
      cy.wait(1000)
      cy.goToStudioFromToolbar()

    })

    it('[In Studio] Hides ghost instance info box to ensure out of way for instance templates', () => {
      cy.get('[data-cy=more_button]').click({force: true});
      cy.wait(100)
      cy.get('[data-cy=advanced_setting]').click({force: true})
      cy.wait(100)
      cy.get('[data-cy=show_ghost_instances]').click({force: true})
    })

    it('[In Studio] Selects a Created Instance Template', () => {
      cy.wait(2000);
      cy.get('[data-cy="instance-type-select"]').click({force: true})
      cy.wait(1000);
      cy.get('.v-list.v-select-list div').contains('template').click({force: true})
    })

    it('[In Studio] Draws a Created Instance Template', () => {

      cy.mousedowncanvas(75, 75);
      cy.mouseupcanvas(75, 75);

      cy.mousemovecanvas(250, 250);
      cy.mousedowncanvas(250, 250);
      cy.mouseupcanvas(250, 250);

    })
  })
})
