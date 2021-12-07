import testUser from '../../../fixtures/users.json';

describe('Annotation 3D Interface display', () => {
  let main_canvas_container = 'main_screen';
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
      cy.wait(5000)

      cy.get('[data-cy=edit_toggle]').click({force: true})
      cy.get(`[data-cy=${main_canvas_container}]`).click({force: true})
      cy.wait(2000)
      cy.draw_cuboid_3d(100, 100, 50, 50, main_canvas_container)


    })

    it('Saves the Files', () => {
      cy.get('[data-cy="save_button"]').click({force: true})


    })

    it('Deletes the Cuboid', () => {
      cy.get(`[data-cy=${main_canvas_container}]`).trigger('keydown', { keyCode: 46, which: 46 })
      cy.wait(500)
      cy.get('[data-cy="save_button"]').click({force: true})
    })

  })
})
