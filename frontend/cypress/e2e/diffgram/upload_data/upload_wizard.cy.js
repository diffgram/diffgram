import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';


describe('Upload Wizard Spec Tests', () => {

  context('Upload Wizard Main Features', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password);
      cy.gotToProject(testUser.project_string_id);
      cy.createLabels(testLabels)
      cy.visit(`http://localhost:8085/studio/upload/${testUser.project_string_id}`);
    })
    //
    // context('It Uploads and Views an image with no labels', () => {
    //   it('Correctly uploads an image on the wizard', () => {
    //     cy.uploadAndViewSampleImage(testUser.project_string_id);
    //   })
    // })


    context('It Uploads and Views an image labeled data', () => {
      it('Correctly uploads an image on the wizard', () => {
        cy.loginByForm(testUser.email, testUser.password);
        cy.gotToProject(testUser.project_string_id);
        cy.uploadImageWithLabels(testUser.project_string_id);
      })
    })
  })

})
