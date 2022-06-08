import testUser from '../../../fixtures/users.json';
import testLabels from "../../../fixtures/labels.json";

describe('Annotation Text Interface display', () => {

  context('Text Interface display', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password);
      cy.gotToProject(testUser.project_string_id);
      cy.createLabels(testLabels)

    })

    it('Creates text token instances', () => {
      cy.upload_text_file(testUser.project_string_id);
      cy.wait(500)
      cy.get('[data-cy="token_1_line_1"]').should('be.visible');
      cy.get('[data-cy="token_1_line_1"]').realMouseDown().realMouseUp();
      cy.realType("1");
      cy.realType("{esc}");
      cy.get('[data-cy="token_3_line_2"]').should('be.visible');
      cy.get('[data-cy="token_3_line_2"]').realMouseDown().realMouseUp();
      cy.realType("2");
    })
  })
})
