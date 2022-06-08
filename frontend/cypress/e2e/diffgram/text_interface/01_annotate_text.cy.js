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
      cy.get('[data-cy="text_label_0"]').should('be.visible')
      cy.realType("{esc}");
      cy.get('[data-cy="token_3_line_2"]').should('be.visible');
      cy.get('[data-cy="token_3_line_2"]').realMouseDown().realMouseUp();
      cy.realType("2");
      cy.get('[data-cy="text_label_1"]').should('be.visible')
    })
    
    it('Creates relations between text tokens', () => {     
      cy.wait(500) 
      cy.get('[data-cy="text_label_0"]').click({force: true})
      cy.get('[data-cy="text_label_1"]').click({force: true})
      cy.realType("3");
      cy.get('[data-cy="text_label_2"]').should('be.visible')
    })

    it('Deletes instance from the context menu', () => {
      cy.wait(500) 
      cy.get('[data-cy="text_label_0"]').rightclick({force: true})
      cy.get('[data-cy="delete-instance-from-context"]').click({force: true})
      cy.get('[data-cy="text_label_1"]').should('not.exist')
      cy.get('[data-cy="text_label_2"]').should('not.exist')
    })

    it('Successfully undo delete command', () => {
      cy.wait(500)
      cy.get('[data-cy="undo"]').click({force: true})
      cy.get('[data-cy="text_label_1"]').should('be.visible')
      cy.get('[data-cy="text_label_2"]').should('be.visible')
    })
  })
})
