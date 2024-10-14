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

    before(() => { // use before instead of before(function ()
      Cypress.Cookies.debug(true, {verbose: true})
      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)
    })

    afterEach(() => { // add this to clear any stored cookies after each test
      cy.clearCookies();
    })

    it('Correctly creates Compound Global Attribute', () => {
      cy.createCompoundGlobalAttribute(prompt, 'radio', options)
    })

    it('Correctly uploads a compound file and display the global compound attribute.', () => {
      const fileUuid = uuidv4();
      cy.uploadCompoundFileImages(testUser.project_string_id,  `${fileUuid}.diffgram`, 2)
        .wait(3000)
        .get('[data-cy="global-attributes-compound-list"]').should('exist')
    })

    it('Correctly sets the value of the radio button compound file attribute.', () => {
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
          expect(response.statusCode, 'response status').to.eq(200)
        })
    })

  })
})
