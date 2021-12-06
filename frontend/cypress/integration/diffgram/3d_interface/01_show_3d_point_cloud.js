import testUser from '../../../fixtures/users.json';

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

    it('Displays a 3D file', () => {
      cy.upload_3d_file();
    })

    it('Displays the toolbar on the 3D Interface', () => {

    })

    it('Displays the instance list detail on the left panel', () => {

    })
  })
})
