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

    it('Draws a 3D Cuboid', () => {
      cy.upload_3d_file(testUser.project_string_id);



    })

    it('Saves the Files', () => {



    })

    it('Deletes the Cuboid', () => {


    })

  })
})
