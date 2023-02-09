import testUser from '../../../fixtures/users.json';
import {v4 as uuidv4} from "uuid";

describe('Global Compound Attributes Tests', () => {

  context('Global Compound Attributes Tests Creation & Save', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)
        .uploadCompoundFileImages(testUser.project_string_id,  `${uuidv4()}.diffgram`, 2)

    })

    it('Correctly creates Compound Global Attribute', () => {
        cy.createCompoundGlobalAttribute('compound global radio button', 'radio')
    })
  })
})
