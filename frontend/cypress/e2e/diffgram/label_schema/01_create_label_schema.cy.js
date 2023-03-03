import testUser from '../../../fixtures/users.json';
import testLabels from "../../../fixtures/labels.json";

describe('Label Schemas Management', () => {
  let name = 'test_schema'
  context('Label Schemas Management', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})

      // login before all tests
      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)

    })

    it('Creates a label Schema', () => {
      cy.createLabelSchema(name)
        .get(`[data-cy="schema_item__${name}"]`).first().should('be.visible')
    })

    it('Correctly displays tabbed component', () => {
      cy.get(`[data-cy="tab__Labels"]`).first().should('be.visible')
      cy.get(`[data-cy="tab__Attributes"]`).first().should('be.visible')
      cy.get(`[data-cy="tab__Geometries"]`).first().should('be.visible')
    })

    it('Correctly Edits Schema Name', () => {
      cy.get(`[data-cy="schema_item__${name}"]`).first().click({force: true})
        .get(`[data-cy="edit_schema_name_button"]`).first().click({force: true})
        .get(`[data-cy="schema_name_text_field"]`).type(`{selectall}{backspace}Updated Schema Name`)
        .get(`[data-cy="save_name_button"]`).first().click({force: true})
        .get(`[data-cy="schema_item__Updated Schema Name"]`).first().should('be.visible')
    })
    it('Correctly Archives a Schema', () => {
      let url = `/api/v1/project/*/labels-schema/*/update`
      cy.intercept(url).as('update_schema')
      cy.get(`[data-cy="schema_item__Updated Schema Name"]`).first().click({force: true})
        .get(`[data-cy="archive_schema_button"]`).first().click({force: true})
        .get(`[data-cy="archive_schema_button_confirm"]`).first().click({force: true})
        .wait('@update_schema').its('response').should('have.property', 'statusCode', 200)

    })
  })
})
