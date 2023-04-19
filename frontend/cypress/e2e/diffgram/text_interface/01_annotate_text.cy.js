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
      cy.upload_text_file(testUser.project_string_id)
        .wait(3000)
      cy.get('[data-cy="token_1_line_1"]').should('be.visible')
        .get('[data-cy="token_1_line_1"]').realMouseDown().realMouseUp()
        .wait(500)
        .realType("1")
        .wait(500)
        .get('[data-cy="text_label_0"]').should('be.visible')
        .realType("{esc}")
        .get('[data-cy="token_3_line_2"]').should('be.visible')
        .get('[data-cy="token_3_line_2"]').realMouseDown().realMouseUp()
        .realType("2")
        .get('[data-cy="text_label_1"]').should('be.visible')
    })

    it('Creates relations between text tokens', () => {
      cy.wait(500)
        .get('[data-cy="text_label_0"]').click({force: true})
        .get('[data-cy="text_label_1"]').click({force: true})
        .realType("3")
        .get('[data-cy="text_label_2"]').should('be.visible')
    })

    it('Deletes instance from the context menu', () => {
      cy.wait(500)
        .get('[data-cy="text_label_0"]').click({force: true})
        .get('[data-cy="text_label_0"]').rightclick({force: true})
        .get('[data-cy="delete-instance-from-context"]').click({force: true})
        .get('[data-cy="text_label_1"]').should('not.exist')
        .get('[data-cy="text_label_2"]').should('not.exist')
    })

    it('Successfully undo delete command', () => {
      cy.wait(500)
        .get('[data-cy="undo"]').click({force: true})
        .get('[data-cy="text_label_1"]').should('be.visible')
        .get('[data-cy="text_label_2"]').should('be.visible')
    })

    it('Successfully redo delete command', () => {
      cy.wait(500)
        .get('[data-cy="redo"]').click({force: true})
        .get('[data-cy="text_label_1"]').should('not.exist')
        .get('[data-cy="text_label_2"]').should('not.exist')
    })

    it('Should update instance label', () => {
      cy.wait(500)
        .get('[data-cy="instance-expansion-panel"]').realClick()
        .get('[data-cy="label_name_0"]').invoke("text")
        .get('[data-cy="change_label_0"]').click({force: true})
        .get('[data-cy="select_text_label"]').click({force: true})
        .wait(500)
        .realPress("ArrowUp")
        .realPress("Enter");
    })
  })
})
