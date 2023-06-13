import testUser from '../../../fixtures/users.json';
import {v4 as uuidv4} from "uuid";

describe('Global Compound Attributes Tests', () => {

  context('Global Compound Attributes Tests Creation & Save', () => {
    const prompt = 'compound global radio button'
    const options =  [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ]
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)

    })

    it('Correctly creates Compound Global Attribute', () => {
      cy.createCompoundGlobalAttribute(prompt, 'radio', options)
    })
    it('Correctly uploads a compound file and display the global compound attribute.', () => {

      return // https://github.com/diffgram/diffgram/issues/1392
      cy.uploadCompoundFileImages(testUser.project_string_id,  `${uuidv4()}.diffgram`, 2)
        .wait(3000)
        .get('[data-cy="global-attributes-compound-list"]').should('exist')
    })

    it('Correctly sets the value of the radio button compound file attribute.', () => {
      return
      // Select The Attribute
      cy.get(`[data-cy="attribute_group_header_${prompt}"]`).first().click({force: true});
      cy.get(`[data-cy="${prompt}_radio_${options[3]}"]`).first().click({force: true})
      // Save The attribute
      cy.intercept(`api/project/*/file/*/annotation/update`).as('annotation_update')
      cy.get('body').type('{esc}');

      cy.get('[data-cy="save_button"]').click({force: true})
      cy.wait('@annotation_update')
        .should(({request, response}) => {
          expect(request.method).to.equal('POST')
          // it is a good practice to add assertion messages
          // as the 2nd argument to expect()
          expect(response.statusCode, 'response status').to.eq(200)
        })
    })

  })
})
