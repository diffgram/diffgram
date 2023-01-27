import testUser from '../../../fixtures/users.json';
import testLabels from "../../../fixtures/labels.json";

describe('Annotation Text Interface display', () => {

  context('Text Interface display', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})

      // login before all tests
      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)
        .createLabels(testLabels)

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

    it('Successfully redo delete command', () => {
      cy.wait(500)
      cy.get('[data-cy="redo"]').click({force: true})
      cy.get('[data-cy="text_label_1"]').should('not.exist')
      cy.get('[data-cy="text_label_2"]').should('not.exist')
    })

    it('Should update instance label', () => {
      cy.wait(500)
      cy.get('[data-cy="instance-expansion-panel"]').realClick()
      cy.get('[data-cy="label_name_0"]').invoke("text")
      cy.get('[data-cy="change_label_0"]').click({force: true})
      cy.get('[data-cy="select_text_label"]').click({force: true})
      cy.wait(500)
      cy.realPress("ArrowUp");
      cy.realPress("Enter");
    })
  })
})
