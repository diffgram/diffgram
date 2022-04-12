import testUser from '../../../fixtures/users.json';
import testLabels from "../../../fixtures/labels.json";

describe('Annotation 3D Interface display', () => {

  context('3D Interface display', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password);
      cy.gotToProject(testUser.project_string_id);

    })
    it('Correctly display tabbed component', () => {
      cy.get(`[data-cy="tab__Labels"]`).first().should('be.visible')
      cy.get(`[data-cy="tab__Attributes"]`).first().should('be.visible')
      cy.get(`[data-cy="tab__Geometries"]`).first().should('be.visible')
    })
    it('Creates a label Schema', () => {
      let name = 'test_schema'
      cy.createLabelSchema(name)
      cy.get(`[data-cy="schema_item__${name}"]`).first().should('be.visible')
    })
  })
})
