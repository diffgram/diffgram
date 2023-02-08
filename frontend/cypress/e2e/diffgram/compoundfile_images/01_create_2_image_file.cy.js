import testUser from '../../../fixtures/users.json';
import {v4 as uuidv4} from "uuid";

describe('Create 2 image compound file', () => {

  context('2 Images Compound File Creation', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)
        .uploadCompoundFileImages(testUser.project_string_id,  `${uuidv4()}.diffgram`, 2)

    })

    it('Correctly Renders 2 panels for compound file.', () => {
      cy.createInstanceTemplate('instance template 1', {
        nodes: [{x: 100, y: 100}, {x: 300, y: 300}, {x: 400, y: 400}, {x: 75, y: 150}],
        edges: [[0, 1], [0, 2], [0, 3]],
      });
      cy.get('[data-cy=save_instance_template_button]').click({force: true});
      cy.wait(5000);
    })
  })
})
