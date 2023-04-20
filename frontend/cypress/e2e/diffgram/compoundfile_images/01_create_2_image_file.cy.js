import testUser from '../../../fixtures/users.json';
import {v4 as uuidv4} from "uuid";

describe('Create 2 image compound file', () => {

  context('2 Images Compound File Creation', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)


    })

    it('Correctly Renders 2 panels for compound file.', () => {
      cy.uploadCompoundFileImages(testUser.project_string_id,  `${uuidv4()}.diffgram`, 2)

        .wait(6000).get('.pane-container').should('have.length', 2)
    })
  })
})
