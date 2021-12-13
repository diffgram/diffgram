import testUser from '../../../fixtures/users.json';

const points = [
    {x: 200, y: 25},
    {x: 200, y: 60},
    {x: 180, y: 40},
    {x: 160, y: 10},
    {x: 200, y: 25},
    ]

describe('Autoborder', () => {

  context('Autoborder', () => {

    before(function () {

      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      // Straight to studio from login
      cy.loginByForm(testUser.email, testUser.password, "?redirect=%2Fstudio%2Fannotate%2Fdiffgram-testing-e2e");
      cy.uploadAndViewSampleImage(testUser.project_string_id);
      cy.uploadAndViewSampleImage(testUser.project_string_id);
      cy.wait(15000)
    })

    it('[Prep] Create a Polygon to Prepare', () => {
      cy.selectDrawValidatePolygon(points)
    })

    it('[UI] Shows General Info Prompt', () => {
      cy.get('[data-cy="ok_autoborder"]').click({force: true})
    })

    it('[Canvas] New Polygon & Selects First Autoborder Point', () => {
      cy.mousedowncanvas(points[0].x + 5, points[0].y + 5);
      cy.mouseupcanvas()

      cy.mousedowncanvas(points[0].x, points[0].y);
      cy.mouseupcanvas()
    })

    /*
    it('[UI] Shows Point Selected Usage Prompt', () => {
     cy.get('[data-cy="minimize-file-explorer-button"]')
      .then($button => {
          console.log($button)
          if ($button.is(':visible')) {
              $button.click()
            }
          })
      cy.get('[data-cy="auto_border_first_point_selected_usage_prompt"]').should('be.visible')
    })
    */

    it('[Canvas] Selects Second Autoborder Point', () => {
      cy.mousedowncanvas(points[2].x, points[2].y);
      cy.mouseupcanvas()
    })

    it('[UI] Shows Second Prompt', () => {
      cy.get('[data-cy="auto_border_path_prompt"]').should('be.visible')
    })

    it('[UI] Selects Short Path', () => {
      cy.get('[data-cy="auto_border_path_prompt_short"]').should('be.visible')
      cy.get('[data-cy="auto_border_path_prompt_short"]').click()
    })

  })
})
